import functools
import datetime
import calendar
from struct import pack

from types import NoneType
from mustaine.protocol import Call, Object, Remote, Binary

from .utils import toposort

# Implementation of Hessian 1.0.2 serialization
#   see: http://hessian.caucho.com/doc/hessian-1.0-spec.xtp

RETURN_TYPES = {
    NoneType: 'null',
    bool: 'bool',
    int: 'int',
    long: 'long',
    float: 'double',
    datetime.datetime: 'date',
    Binary: 'binary',
    Remote: 'remote',
    Call: 'call',
    str: 'string',
    unicode: 'string',
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
    sorted_classes = reversed(toposort.toposort_flatten(mro_dict))
    return [type_encoders[cls] for cls in sorted_classes if cls in type_encoders]


class EncoderBase(type):

    def __new__(cls, name, bases, attrs):
        encoders = []
        for base in bases:
            if hasattr(base, '_mustaine_encoders'):
                encoders.extend(base._mustaine_encoders)
        for k, v in attrs.iteritems():
            if isinstance(v, encoder_method_wrapper):
                encoders.append(v)
        attrs['_mustaine_encoders'] = sort_mro(encoders)
        return super(EncoderBase, cls).__new__(cls, name, bases, attrs)


class Encoder(object):

    __metaclass__ = EncoderBase

    def _encode(self, obj):
        encoder = None
        for e in self._mustaine_encoders:
            if isinstance(obj, e.data_type):
                encoder = e
                break
        if not encoder:
            raise TypeError("mustaine.encoder cannot serialize %s" % (type(obj),))
        return encoder(self, obj)

    def encode(self, obj):
        return self._encode(obj)[1]

    def encode_arg(self, obj):
        return self._encode(obj)

    @encoder_for(NoneType)
    def encode_null(self, _):
        return 'N'

    @encoder_for(bool)
    def encode_boolean(self, value):
        if value:
            return 'T'
        else:
            return 'F'

    @encoder_for(int)
    def encode_int(self, value):
        return pack('>cl', 'I', value)

    @encoder_for(long)
    def encode_long(self, value):
        return pack('>cq', 'L', value)

    @encoder_for(float)
    def encode_double(self, value):
        return pack('>cd', 'D', value)

    @encoder_for(datetime.datetime)
    def encode_date(self, value):
        return pack('>cq', 'd', int(calendar.timegm(value.timetuple())) * 1000)

    @encoder_for(str)
    def encode_string(self, value):
        encoded = ''

        try:
            value = value.encode('ascii')
        except UnicodeDecodeError:
            raise TypeError(
                "mustaine.encoder cowardly refuses to guess the encoding for "
                "string objects containing bytes out of range 0x00-0x79; use "
                "Binary or unicode objects instead")

        while len(value) > 65535:
            encoded += pack('>cH', 's', 65535)
            encoded += value[:65535]
            value    = value[65535:]

        encoded += pack('>cH', 'S', len(value.decode('utf-8')))
        encoded += value
        return encoded

    @encoder_for(unicode)
    def encode_unicode(self, value):
        encoded = ''

        while len(value) > 65535:
            encoded += pack('>cH', 's', 65535)
            encoded += value[:65535].encode('utf-8')
            value    = value[65535:]

        encoded += pack('>cH', 'S', len(value))
        encoded += value.encode('utf-8')
        return encoded

    @encoder_for(list)
    def encode_list(self, obj):
        encoded = ''.join(map(self.encode, obj))
        return pack('>2cl', 'V', 'l', -1) + encoded + 'z'

    @encoder_for(tuple)
    def encode_tuple(self, obj):
        encoded = ''.join(map(self.encode, obj))
        return pack('>2cl', 'V', 'l', len(obj)) + encoded + 'z'

    def encode_keyval(self, pair):
        return ''.join((self.encode(pair[0]), self.encode(pair[1])))

    @encoder_for(dict)
    def encode_map(self, obj):
        encoded = ''.join(map(self.encode_keyval, obj.items()))
        return pack('>c', 'M') + encoded + 'z'

    @encoder_for(Object)
    def encode_mobject(self, obj):
        obj_type = '.'.join([type(obj).__module__, type(obj).__name__])
        encoded  = pack('>cH', 't', len(obj_type)) + obj_type
        members  = obj.__getstate__()
        encoded += ''.join(map(self.encode_keyval, members.items()))
        return (type(obj).__name__, pack('>c', 'M') + encoded + 'z')

    @encoder_for(Remote)
    def encode_remote(self, obj):
        encoded = self.encode_string(obj.url)
        return pack('>2cH', 'r', 't', len(obj.type_name)) + obj.type_name + encoded

    @encoder_for(Binary)
    def encode_binary(self, obj):
        encoded = ''
        value   = obj.value

        while len(value) > 65535:
            encoded += pack('>cH', 'b', 65535)
            encoded += value[:65535]
            value    = value[65535:]

        encoded += pack('>cH', 'B', len(value))
        encoded += value

        return encoded

    @encoder_for(Call)
    def encode_call(self, call):
        method    = call.method
        headers   = ''
        arguments = ''

        for header,value in call.headers.items():
            if not isinstance(header, str):
                raise TypeError("Call header keys must be strings")

            headers += pack('>cH', 'H', len(header)) + header
            headers += self.encode(value)

        for arg in call.args:
            data_type, arg = self.encode_arg(arg)
            if call.overload:
                method    += '_' + data_type
            arguments += arg

        encoded  = pack('>cBB', 'c', call.version, 0)
        encoded += headers
        encoded += pack('>cH', 'm', len(method)) + method
        encoded += arguments
        encoded += 'z'

        return encoded


encoder = Encoder()


def encode_object(obj):
    return encoder.encode(obj)
