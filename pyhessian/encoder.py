import re
import functools
import datetime
import calendar
import operator
from struct import pack

import six
from six.moves import reduce

from pyhessian.protocol import Call, Object, Remote, Binary

from .utils import toposort_flatten
from .data_types import long

# Implementation of Hessian 1.0.2 serialization
#   see: http://hessian.caucho.com/doc/hessian-1.0-spec.xtp

RETURN_TYPES = {
    type(None): 'null',
    bool: 'bool',
    int: 'int',
    long: 'long',
    float: 'double',
    datetime.datetime: 'date',
    Binary: 'binary',
    Remote: 'remote',
    Call: 'call',
    str: 'string',
    six.text_type: 'string',
    list: 'list',
    tuple: 'list',
    dict: 'map',
}


class bound_function_wrapper(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __call__(self, *args, **kwargs):
        return self.wrapped(*args, **kwargs)


class encoder_method_wrapper(object):

    def __init__(self, wrapped, data_type):
        self.wrapped = wrapped
        self.data_type = data_type
        functools.update_wrapper(self, wrapped)

    def __call__(self, *args, **kwargs):
        return self.wrapped(*args, **kwargs)

    def __get__(self, instance, owner):
        wrapped = self.wrapped.__get__(instance, owner)
        return bound_function_wrapper(wrapped)


def encoder_for(data_type, version=1, return_type=None):
    return_type = RETURN_TYPES.get(data_type)

    def wrap(f):
        @functools.wraps(f)
        def wrapper(*args):
            if return_type:
                return return_type, f(*args)
            else:
                return f(*args)
        return encoder_method_wrapper(wrapper, data_type)

    return wrap


def sort_mro(encoders):
    """
    Sort encoders so that subclasses precede the types they extend when
    checking isinstance(value, encoder_data_type). This way, the encoder
    will (for instance) check whether isinstance(value, bool) before it
    checks isinstance(value, int), which is necessary because bool is a
    subclass of int.
    """
    type_encoders = dict([[e.data_type, e] for e in encoders])
    mro_dict = dict([[k, set(k.mro()[1:])] for k in type_encoders.keys()])
    sorted_classes = reversed(toposort_flatten(mro_dict, sort=False))
    return [type_encoders[cls] for cls in sorted_classes if cls in type_encoders]


class EncoderBase(type):

    def __new__(cls, name, bases, attrs):
        encoders = []
        for base in bases:
            if hasattr(base, '_hessian_encoders'):
                encoders.extend(base._hessian_encoders)
        for k, v in six.iteritems(attrs):
            if isinstance(v, encoder_method_wrapper):
                encoders.append(v)
        attrs['_hessian_encoders'] = sort_mro(encoders)
        return super(EncoderBase, cls).__new__(cls, name, bases, attrs)


@six.add_metaclass(EncoderBase)
class Encoder(object):

    def __init__(self):
        self._refs = []

    def _encode(self, obj):
        encoder = None
        for e in self._hessian_encoders:
            if isinstance(obj, e.data_type):
                encoder = e
                break
        if not encoder:
            raise TypeError("pyhessian.encoder cannot serialize %s" % (type(obj),))
        return encoder(self, obj)

    def add_ref(self, obj):
        """
        Add an object to the reference list. Returns None if the object
        has not yet been referenced, or the encoding of the reference
        if it has.
        """
        if id(obj) in self._refs:
            return pack('>cl', b'R', self._refs.index(id(obj)))

        self._refs.append(id(obj))

    def encode(self, obj):
        return self._encode(obj)[1]

    def encode_arg(self, obj):
        return self._encode(obj)

    @encoder_for(type(None))
    def encode_null(self, _):
        return b'N'

    @encoder_for(bool)
    def encode_boolean(self, value):
        if value:
            return b'T'
        else:
            return b'F'

    @encoder_for(int)
    def encode_int(self, value):
        return pack('>cl', b'I', value)

    @encoder_for(long)
    def encode_long(self, value):
        return pack('>cq', b'L', value)

    @encoder_for(float)
    def encode_double(self, value):
        return pack('>cd', b'D', value)

    @encoder_for(datetime.datetime)
    def encode_date(self, value):
        return pack('>cq', b'd', int(calendar.timegm(value.timetuple())) * 1000)

    try:
        # UCS-4
        high_codepoints_re = re.compile(u'([\U00010000-\U0010ffff])', re.UNICODE)
    except re.error:
        # UCS-2
        high_codepoints_re = re.compile(u'([\uD800-\uDBFF][\uDC00-\uDFFF])')

    def _unicode_encode(self, value):
        """
        Encode the value to unicode, splitting high plane codepoints into
        surrogate pairs.
        """
        splits = self.high_codepoints_re.split(value)
        enc_value = b''
        str_len = 0
        for s in splits:
            if self.high_codepoints_re.match(s):
                str_len += 2
                enc_value += self._encode_to_surrogate_pair(s)
            else:
                str_len += len(s)
                enc_value += s.encode('utf-8')
        return str_len, enc_value

    def _encode_to_surrogate_pair(self, char):
        if len(char) == 2:
            s = char[0].encode('utf-8') + char[1].encode('utf-8')
        else:
            code = ord(char) - 0x10000
            c1 = six.unichr(0xD800 | (code >> 10))
            c2 = six.unichr(0xDC00 | (code & 0x3FF))
            if six.PY2:
                s = c1.encode('utf-8') + c2.encode('utf-8')
            else:
                s = (c1.encode('utf-8', 'surrogatepass')
                    + c2.encode('utf-8', 'surrogatepass'))
        return s

    @encoder_for(six.text_type)
    def encode_unicode(self, value):
        encoded = b''

        while len(value) > 32767:
            str_len, enc_value = self._unicode_encode(value[:32767])
            encoded += pack('>cH', b's', str_len)
            encoded += enc_value
            value = value[32767:]

        str_len, enc_value = self._unicode_encode(value)
        encoded += pack('>cH', b'S', str_len)
        encoded += enc_value

        return encoded

    if six.PY2:
        @encoder_for(str)
        def encode_string(self, value):
            encoded = b''

            try:
                value = value.encode('ascii')
            except UnicodeDecodeError:
                raise TypeError(
                    "pyhessian.encoder cowardly refuses to guess the encoding for "
                    "string objects containing bytes out of range 0x00-0x79; use "
                    "Binary or unicode objects instead")

            while len(value) > 65535:
                encoded += pack('>cH', b's', 65535)
                encoded += value[:65535]
                value = value[65535:]

            encoded += pack('>cH', b'S', len(value.decode('utf-8')))
            encoded += value
            return encoded

    @encoder_for(list)
    def encode_list(self, obj):
        ref = self.add_ref(obj)
        if ref:
            return ref
        encoded = reduce(operator.add, map(self.encode, obj), b'')
        return pack('>2cl', b'V', b'l', -1) + encoded + b'z'

    @encoder_for(tuple)
    def encode_tuple(self, obj):
        ref = self.add_ref(obj)
        if ref:
            return ref
        encoded = reduce(operator.add, map(self.encode, obj), b'')
        return pack('>2cl', b'V', b'l', len(obj)) + encoded + b'z'

    def encode_keyval(self, pair):
        return self.encode(pair[0]) + self.encode(pair[1])

    @encoder_for(dict)
    def encode_map(self, obj):
        ref = self.add_ref(obj)
        if ref:
            return ref
        keyvals = map(self.encode_keyval, obj.items())
        encoded = reduce(operator.add, keyvals, b'')
        return pack('>c', b'M') + encoded + b'z'

    @encoder_for(Object)
    def encode_mobject(self, obj):
        ref = self.add_ref(obj)
        if ref:
            return (type(obj).__name__, ref)
        obj_type = '.'.join([type(obj).__module__, type(obj).__name__])
        encoded = pack('>cH', b't', len(obj_type)) + six.b(obj_type)
        members = obj.__getstate__()
        keyvals = map(self.encode_keyval, members.items())
        encoded += reduce(operator.add, keyvals, b'')
        return (type(obj).__name__, pack('>c', b'M') + encoded + b'z')

    @encoder_for(Remote)
    def encode_remote(self, obj):
        ref = self.add_ref(obj)
        if ref:
            return ref
        encoded = self.encode_string(obj.url)
        return pack('>2cH', b'r', b't', len(obj.type_name)) + obj.type_name + encoded

    @encoder_for(Binary)
    def encode_binary(self, obj):
        encoded = b''
        value = obj.value

        while len(value) > 65535:
            encoded += pack('>cH', b'b', 65535)
            encoded += value[:65535]
            value = value[65535:]

        encoded += pack('>cH', b'B', len(value))
        encoded += value

        return encoded

    @encoder_for(Call)
    def encode_call(self, call):
        method = call.method
        headers = b''
        arguments = b''

        for header, value in call.headers.items():
            if not isinstance(header, str):
                raise TypeError("Call header keys must be strings")

            headers += pack('>cH', b'H', len(header)) + header
            headers += self.encode(value)

        for arg in call.args:
            data_type, arg = self.encode_arg(arg)
            if call.overload:
                method += b'_' + six.b(data_type)
            arguments += arg

        encoded = pack('>cBB', b'c', call.version, 0)
        encoded += headers
        encoded += pack('>cH', b'm', len(method)) + method
        encoded += arguments
        encoded += b'z'

        return encoded


def encode_object(obj):
    encoder = Encoder()
    return encoder.encode(obj)
