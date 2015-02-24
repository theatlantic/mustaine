import datetime
import calendar
from struct import pack

from types import *
from mustaine.protocol import *

# Implementation of Hessian 1.0.2 serialization
#   see: http://hessian.caucho.com/doc/hessian-1.0-spec.xtp

ENCODERS = []
def encoder_for(data_type):
    def register(f):
        # register function `f` to encode type `data_type`
        ENCODERS.append((data_type, f))
        return f
    return register

def returns(data_type):
    def wrap(f):
        # wrap function `f` to return a tuple of (type,data)
        def wrapped(*args):
            return data_type, f(*args)
        return wrapped
    return wrap

def encode_object(obj):
    encoder = None
    for encoder_type, encoder_func in ENCODERS:
        if isinstance(obj, encoder_type):
            encoder = encoder_func
            break
    if not encoder:
        raise TypeError("mustaine.encoder cannot serialize %s" % (type(obj),))

    return encoder(obj)[1]


@encoder_for(NoneType)
@returns('null')
def encode_null(_):
    return 'N'

@encoder_for(BooleanType)
@returns('bool')
def encode_boolean(value):
    if value:
        return 'T'
    else:
        return 'F'

@encoder_for(IntType)
@returns('int')
def encode_int(value):
    return pack('>cl', 'I', value)

@encoder_for(LongType)
@returns('long')
def encode_long(value):
    return pack('>cq', 'L', value)

@encoder_for(FloatType)
@returns('double')
def encode_double(value):
    return pack('>cd', 'D', value)

@encoder_for(datetime.datetime)
@returns('date')
def encode_date(value):
    return pack('>cq', 'd', int(calendar.timegm(value.timetuple())) * 1000)

@encoder_for(StringType)
@returns('string')
def encode_string(value):
    encoded = ''

    try:
        value = value.encode('ascii')
    except UnicodeDecodeError:
        raise TypeError("mustaine.encoder cowardly refuses to guess the encoding for "
                        "string objects containing bytes out of range 0x00-0x79; use "
                        "Binary or unicode objects instead")

    while len(value) > 65535:
        encoded += pack('>cH', 's', 65535)
        encoded += value[:65535]
        value    = value[65535:]

    encoded += pack('>cH', 'S', len(value.decode('utf-8')))
    encoded += value
    return encoded

@encoder_for(UnicodeType)
@returns('string')
def encode_unicode(value):
    encoded = ''

    while len(value) > 65535:
        encoded += pack('>cH', 's', 65535)
        encoded += value[:65535].encode('utf-8')
        value    = value[65535:]

    encoded += pack('>cH', 'S', len(value))
    encoded += value.encode('utf-8')
    return encoded

@encoder_for(ListType)
@returns('list')
def encode_list(obj):
    encoded = ''.join(map(encode_object, obj))
    return pack('>2cl', 'V', 'l', -1) + encoded + 'z'

@encoder_for(TupleType)
@returns('list')
def encode_tuple(obj):
    encoded = ''.join(map(encode_object, obj))
    return pack('>2cl', 'V', 'l', len(obj)) + encoded + 'z'

def encode_keyval(pair):
    return ''.join((encode_object(pair[0]), encode_object(pair[1])))

@encoder_for(DictType)
@returns('map')
def encode_map(obj):
    encoded = ''.join(map(encode_keyval, obj.items()))
    return pack('>c', 'M') + encoded + 'z'

@encoder_for(Object)
def encode_mobject(obj):
    obj_type = '.'.join([type(obj).__module__, type(obj).__name__])
    encoded  = pack('>cH', 't', len(obj_type)) + obj_type
    members  = obj.__getstate__()

    encoded += ''.join(map(encode_keyval, members.items()))
    return (type(obj).__name__, pack('>c', 'M') + encoded + 'z')

@encoder_for(Remote)
@returns('remote')
def encode_remote(obj):
    encoded = encode_string(obj.url)
    return pack('>2cH', 'r', 't', len(obj.type_name)) + obj.type_name + encoded

@encoder_for(Binary)
@returns('binary')
def encode_binary(obj):
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
@returns('call')
def encode_call(call):
    method    = call.method
    headers   = ''
    arguments = ''

    for header,value in call.headers.items():
        if not isinstance(header, StringType):
            raise TypeError("Call header keys must be strings")

        headers += pack('>cH', 'H', len(header)) + header
        headers += encode_object(value)

    # TODO: this is mostly duplicated at the top of the file in encode_object. dedup
    for arg in call.args:
        encoder = None
        for encoder_type, encoder_func in ENCODERS:
            if isinstance(arg, encoder_type):
                encoder = encoder_func
                break
        if not encoder:
            raise TypeError("mustaine.encoder cannot serialize %s" % (type(arg),))

        data_type, arg = encoder(arg)
        if call.overload:
            method    += '_' + data_type
        arguments += arg

    encoded  = pack('>cBB', 'c', call.version, 0)
    encoded += headers
    encoded += pack('>cH', 'm', len(method)) + method
    encoded += arguments
    encoded += 'z'

    return encoded

