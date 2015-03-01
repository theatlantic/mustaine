import datetime
import operator
from struct import unpack

import six

try:
    from cStringIO import StringIO
except ImportError:
    from six import BytesIO as StringIO

from six.moves import range, reduce

from pyhessian.protocol import (
    Call, Reply, Fault, Binary, Remote, Object, cls_factory)

from .data_types import long


class ParseError(Exception):
    pass


class ListMapTerminator(Exception):
    pass


class Parser(object):

    version = None
    _adapter = None

    def __init__(self):
        self._version_adapters = {
            1: ParserV1,
            2: ParserV2,
        }

    def parse_string(self, string):
        if isinstance(string, six.text_type):
            stream = StringIO(string.encode('utf-8'))
        else:
            stream = StringIO(string)

        return self.parse_stream(stream)

    def parse_stream(self, stream):
        self._result = None

        if hasattr(stream, 'read') and hasattr(stream.read, '__call__'):
            self._stream = stream
        else:
            raise TypeError('Stream parser can only handle objects supporting read()')

        while True:
            code = self._read(1)

            if not self._result:
                if code == b'H' and not self.version:
                    if self._result:
                        raise ParseError('Encountered duplicate type header')
                    self.read_version()

                elif not self.version and code == b'c':
                    self.read_version()
                    self._result = Call(version=self.version)

                elif self.version == 2 and code == b'R':
                    self._result = Reply(version=self.version)

                elif self.version == 2 and code == b'C':
                    method_name = self.read_object()
                    self._result = Call(method=method_name, version=self.version)

                elif not self._result and code == b'r':
                    self.read_version()
                    self._result = Reply(version=self.version)

                elif self.version == 2 and not self._result and code == b'F':
                    self._result = Reply(value=self._adapter._read_fault(),
                        version=self.version)
                    break
                else:
                    raise ParseError("Invalid Hessian message marker: %r" % (code,))
            else:
                if self.version == 1 and code == b'H':
                    key, value = self._read_keyval()
                    self._result.headers[key] = value

                elif self.version == 1 and code == b'm':
                    if not isinstance(self._result, Call):
                        raise ParseError('Encountered illegal method name within reply')

                    if self._result.method:
                        raise ParseError('Encountered duplicate method name definition')

                    self._result.method = self._read(unpack('>H', self._read(2))[0])
                    continue

                elif self.version == 1 and code == b'f':
                    if not isinstance(self._result, Reply):
                        raise ParseError('Encountered illegal fault within call')

                    if self._result.value:
                        raise ParseError('Encountered illegal extra object within reply')

                    self._result.value = self._adapter._read_fault()
                    break

                elif self.version == 1 and code == b'z':
                    break

                else:
                    if isinstance(self._result, Call):
                        if self.version == 2:
                            num_args = self.read_object(code)
                            for i in range(0, num_args):
                                self._result.args.append(self.read_object())
                            break
                        else:
                            self._result.args.append(self.read_object(code))
                    else:
                        if self._result.value:
                            raise ParseError('Encountered illegal extra object within reply')

                        self._result.value = self.read_object(code)
                        if self.version == 2:
                            break

        # have to hit a 'z' to land here, TODO derefs?
        return self._result

    def read_object(self, code=None):
        try:
            return self._adapter._read_object(code)
        except ListMapTerminator:
            raise ParseError("Unhandled list/map terminator code ('Z')")

    def read_version(self):
        version = unpack('<h', self._read(2))[0]
        if version not in self._version_adapters:
            raise ParseError("Encountered unrecognized call version %r" % (version,))
        self._adapter = self._version_adapters[version](base_parser=self)
        self.version = version

    def _read(self, n):
        try:
            r = self._stream.read(n)
        except IOError:
            raise ParseError('Encountered unexpected end of stream')
        except:
            raise
        else:
            if len(r) == 0:
                raise ParseError('Encountered unexpected end of stream')
        return r


class ParserV1(object):
    """
    Implementation of Hessian 1.0.2 deserialization
        see: http://hessian.caucho.com/doc/hessian-1.0-spec.xtp
    """

    version = 1

    def __init__(self, base_parser):
        self._base_parser = base_parser
        self._classdefs = []
        self._refs = []

    def _read(self, n):
        return self._base_parser._read(n)

    def _read_object(self, code=None):
        if code is None:
            code = self._read(1)
        if   code == b'N':
            return None
        elif code == b'T':
            return True
        elif code == b'F':
            return False
        elif code == b'I':
            return int(unpack('>l', self._read(4))[0])
        elif code == b'L':
            return long(unpack('>q', self._read(8))[0])
        elif code == b'D':
            return float(unpack('>d', self._read(8))[0])
        elif code == b'd':
            return self._read_date()
        elif code == b's' or code == b'x':
            fragment = self._read_string()
            next = self._read(1)
            if next.lower() == code:
                return fragment + self._read_object(next)
            else:
                raise ParseError("Expected terminal string segment, got %r" % (next,))
        elif code == b'S' or code == b'X':
            return self._read_string()
        elif code == b'b':
            fragment = self._read_binary()
            next = self._read(1)
            if next.lower() == code:
                return fragment + self._read_object(next)
            else:
                raise ParseError("Expected terminal binary segment, got %r" % (next,))
        elif code == b'B':
            return self._read_binary()
        elif code == b'r':
            return self._read_remote()
        elif code == b'R':
            return self._refs[unpack(">L", self._read(4))[0]]
        elif code == b'V':
            return self._read_list()
        elif code == b'M':
            return self._read_map()
        else:
            raise ParseError("Unknown type marker %r" % (code,))

    def _read_date(self):
        timestamp = unpack('>q', self._read(8))[0]
        return datetime.datetime.utcfromtimestamp(timestamp / 1000)

    def _read_string(self):
        len = unpack('>H', self._read(2))[0]

        bytes = []
        while len > 0:
            byte = self._read(1)
            if ord(byte) in range(0x00, 0x80):
                bytes.append(byte)
            elif ord(byte) in range(0xC2, 0xE0):
                bytes.append(byte + self._read(1))
            elif ord(byte) in range(0xE0, 0xF0):
                bytes.append(byte + self._read(2))
            elif ord(byte) in range(0xF0, 0xF5):
                bytes.append(byte + self._read(3))
            len -= 1

        try:
            return reduce(operator.add, bytes, b'').decode('utf-8')
        except UnicodeDecodeError:
            if six.PY2:
                raise
            # We're possibly dealing with surrogate pairs in Python 3
            return self._decode_byte_array(bytes)

    def _read_binary(self, len=None):
        if len is None:
            len = unpack('>H', self._read(2))[0]
        if len == 0:
            return Binary(b"")
        return Binary(self._read(len))

    def _read_remote(self):
        r = Remote()
        code = self._read(1)

        if code == b't':
            r.type = self._read(unpack('>H', self._read(2))[0])
            code = self._read(1)
        else:
            r.type = None

        if code != b's' and code != b'S':
            raise ParseError("Expected string object while parsing Remote object URL")

        r.url = self._read_object(code)
        return r

    def _read_list(self, code=None):
        if code is None:
            code = self._read(1)

        if code == b't':
            # read and discard list type
            self._read(unpack('>H', self._read(2))[0])
            code = self._read(1)

        fixed_length = False

        if code == b'l':
            # read and discard list length
            self._read(4)
            code = self._read(1)
            fixed_length = True

        result = []
        self._refs.append(result)

        while code != b'z':
            result.append(self._read_object(code))
            code = self._read(1)

        if fixed_length:
            return tuple(result)
        else:
            return result

    def _read_map(self):
        code = self._read(1)

        if code == b't':
            type_len = unpack('>H', self._read(2))[0]
            if type_len > 0:
                # a typed map deserializes to an object
                result = cls_factory(self._read(type_len))()
            else:
                result = {}

            code = self._read(1)
        else:
            # untyped maps deserialize to a dict
            result = {}

        self._refs.append(result)

        fields = {}
        while code != b'z':
            key, value = self._read_keyval(code)

            if isinstance(result, Object):
                fields[str(key)] = value
            else:
                fields[key] = value

            code = self._read(1)

        if isinstance(result, Object):
            result.__setstate__(fields)
        else:
            result.update(fields)

        return result

    def _read_fault(self):
        fault = self._read_map()
        return Fault(fault['code'], fault['message'], fault.get('detail'))

    def _read_keyval(self, first=None):
        key = self._read_object(first or self._read(1))
        value = self._read_object(self._read(1))

        return key, value

    def _decode_byte_array(self, bytes):
        s = ''
        while(len(bytes)):
            b, bytes = bytes[0], bytes[1:]
            if six.PY2:
                c = b.decode('utf-8')
            else:
                c = b.decode('utf-8', 'surrogatepass')
                if '\uD800' <= c <= '\uDBFF':
                    b, bytes = bytes[0], bytes[1:]
                    c2 = b.decode('utf-8', 'surrogatepass')
                    c = self._decode_surrogate_pair(c, c2)
            s += c
        return s

    def _decode_surrogate_pair(self, c1, c2):
        """
        Python 3 no longer decodes surrogate pairs for us; we have to do it
        ourselves.
        """
        if not('\uD800' <= c1 <= '\uDBFF') or not ('\uDC00' <= c2 <= '\uDFFF'):
            raise Exception("Invalid UTF-16 surrogate pair")
        code = 0x10000
        code += (ord(c1) & 0x03FF) << 10
        code += (ord(c2) & 0x03FF)
        return chr(code)


class ParserV2(ParserV1):
    """
    Implementation of Hessian 2.0 Serialization Protocol
        see: http://hessian.caucho.com/doc/hessian-serialization.html
    """

    version = 2

    def _read_object(self, code=None):
        if code is None:
            code = self._read(1)

        if b'\x00' <= code <= b'\x1F':
            # utf-8 string length 0-32
            return self._read_compact_string(code)
        elif b'\x20' <= code <= b'\x2F':
            # binary data length 0-16
            return self._read_binary(code)
        elif b'\x30' <= code <= b'\x33':
            # utf-8 string length 0-1023
            return self._read_compact_string(code)
        elif b'\x34' <= code <= b'\x37':
            # binary data length 0-1023
            return self._read_binary(code)
        elif b'\x38' <= code <= b'\x3F':
            # three-octet compact long (-x40000 to x3ffff)
            b2 = (ord(code) - 0x3c) << 16
            b1 = ord(self._read(1)) << 8
            b0 = ord(self._read(1))
            return long(b0 + b1 + b2)
        elif code in (b'\x41', b'\x42'):
            # 8-bit binary data non-final chunk ('A')
            # 8-bit binary data final chunk ('B')
            return self._read_binary(code)
        elif code == b'\x43':
            # object type definition ('C')
            self._read_class_def()
            return self._read_object()
        elif code == b'\x48':
            # untyped map ('H')
            return self._read_map()
        elif code == b'\x4A':
            # 64-bit UTC millisecond date ('J')
            return self._read_date()
        elif code == b'\x4B':
            # 32-bit UTC minute date ('K')
            return self._read_compact_date()
        elif code == b'\x4D':
            # map with type ('M')
            return self._read_map(code)
        elif code == b'\x4F':
            # object instance ('O')
            return self._read_class_object(code)
        elif code == b'\x51':
            # reference to map/list/object - integer ('Q')
            return self._refs[self._read_object()]
        elif code in (b'\x52', b'\x53'):
            # utf-8 string non-final chunk ('R')
            # utf-8 string final chunk ('S')
            b1 = ord(self._read(1)) << 8
            b0 = ord(self._read(1))
            return self._read_v2_string(code, b0 + b1)
        elif code == b'\x55':
            # variable-length list/vector ('U')
            return self._read_list(typed=True, fixed_length=False)
        elif code == b'\x56':
            # fixed-length list/vector ('V')
            return self._read_list(typed=True, fixed_length=True)
        elif code == b'\x57':
            # variable-length untyped list/vector ('W')
            return self._read_list(typed=False, fixed_length=False)
        elif code == b'\x58':
            # fixed-length untyped list/vector ('X')
            return self._read_list(typed=False, fixed_length=True)
        elif code == b'\x59':
            # long encoded as 32-bit int ('Y')
            return long(unpack('>l', self._read(4))[0])
        elif code == b'\x5A':
            # list/map terminator ('Z')
            raise ListMapTerminator()
        elif code == b'\x5B':
            # double 0.0
            return 0.0
        elif code == b'\x5C':
            # double 1.0
            return 1.0
        elif code == b'\x5D':
            # double byte
            return float(unpack('>b', self._read(1))[0])
        elif code == b'\x5E':
            # double short
            return float(unpack('>h', self._read(2))[0])
        elif code == b'\x5F':
            # double represented as float
            return float(unpack('>l', self._read(4))[0] / 1000.0)
        elif b'\x60' <= code <= b'\x6F':
            # object with direct type
            return self._read_class_object(code)
        elif b'\x70' <= code <= b'\x77':
            # fixed list with direct length
            list_len = ord(code) - 0x70
            return self._read_list(typed=True, fixed_length=True, length=list_len)
        elif b'\x78' <= code <= b'\x7F':
            # fixed untyped list with direct length
            list_len = ord(code) - 0x78
            return self._read_list(typed=False, fixed_length=True, length=list_len)
        elif b'\x80' <= code <= b'\xBF':
            # one-octet compact int (-x10 to x3f, x90 is 0)
            return ord(code) - 0x90
        elif b'\xC0' <= code <= b'\xCF':
            # two-octet compact int (-x800 to x7ff)
            return 256 * (ord(code) - 0xc8) + int(unpack('>B', self._read(1))[0])
        elif b'\xD0' <= code <= b'\xD7':
            # three-octet compact int (-x40000 to x3ffff)
            b1 = int(unpack('>B', self._read(1))[0])
            b0 = int(unpack('>B', self._read(1))[0])
            return 65536 * (ord(code) - 0xd4) + 256 * b1 + b0
        elif b'\xD8' <= code <= b'\xEF':
            # one-octet compact long (-x8 to xf, xe0 is 0)
            return long(ord(code) - 0xe0)
        elif b'\xF0' <= code <= b'\xFF':
            # two-octet compact long (-x800 to x7ff, xf8 is 0)
            b1 = (ord(code) - 0xF8) << 8
            b0 = ord(self._read(1))
            return long(b0 + b1)
        else:
            return super(ParserV2, self)._read_object(code)

    def _read_list(self, typed=False, fixed_length=False, length=None):
        if length is 0:
            return tuple([]) if fixed_length else []

        if typed:
            # read and discard list type
            self._read_object()

        result = []
        self._refs.append(result)

        if fixed_length:
            if length is None:
                length = self._read_object()
            while len(result) < length:
                result.append(self._read_object())
        else:
            while True:
                try:
                    obj = self._read_object()
                except ListMapTerminator:
                    break
                else:
                    result.append(obj)

        if fixed_length:
            return tuple(result)
        else:
            return result

    def _read_v2_string(self, code, length):
        if length is 0:
            return u''
        chunks = []
        while True:
            if length is None:
                b1 = ord(self._read(1)) << 8
                b0 = ord(self._read(1))
                length = b0 + b1
            chars = []
            while length > 0:
                char = self._read(1)
                if b'\x00' <= char <= b'\x79':
                    chars.append(char)
                elif b'\xC2' <= char <= b'\xDF':
                    chars.append(char + self._read(1))
                elif b'\xE0' <= char <= b'\xEF':
                    chars.append(char + self._read(2))
                elif b'\xF0' <= char <= b'\xF4':
                    chars.append(char + self._read(3))
                length -= 1

            chunks.append(reduce(operator.add, chars))
            length = None
            if code == b'S':
                break
            try:
                code = self._read(1)
            except ParseError:
                break

        try:
            return reduce(operator.add, chunks, b'').decode('utf-8')
        except UnicodeDecodeError:
            if six.PY2:
                raise
            # We're possibly dealing with surrogate pairs in Python 3
            return self._decode_byte_array(chunks)

    def _read_class_def(self):
        type_name = self._read_object()
        num_fields = self._read_object()
        fields = []
        for i in range(0, num_fields):
            fields.append(self._read_object())
        self._classdefs.append(cls_factory(type_name, fields))

    def _read_class_object(self, code):
        if code == b'O':
            classdef_num = self._read_object()
        else:
            classdef_num = ord(code) - 0x60
        classdef = self._classdefs[classdef_num]
        result = classdef()
        self._refs.append(result)
        field_vals = {}
        for f in classdef._hessian_field_names:
            field_vals[f] = self._read_object()
        result.__setstate__(field_vals)
        return result

    def _read_compact_date(self):
        minutes = unpack('>l', self._read(4))[0]
        return datetime.datetime.utcfromtimestamp(minutes * 60)

    def _read_compact_string(self, code):
        if code >= b'\x30':
            len_bytes = six.b(chr(ord(code) - 0x30)) + self._read(1)
        else:
            len_bytes = b'\x00' + code
        length = unpack('>H', len_bytes)[0]

        bytes = []
        while length > 0:
            byte = self._read(1)
            if b'\x00' <= byte <= b'\x7F':
                bytes.append(byte)
            elif b'\xC2' <= byte <= b'\xDF':
                bytes.append(byte + self._read(1))
            elif b'\xE0' <= byte <= b'\xEF':
                bytes.append(byte + self._read(2))
            elif b'\xF0' <= byte <= b'\xF4':
                bytes.append(byte + self._read(3))
            length -= 1

        try:
            return reduce(operator.add, bytes, b'').decode('utf-8')
        except UnicodeDecodeError:
            if six.PY2:
                raise
            # We're possibly dealing with surrogate pairs in Python 3
            return self._decode_byte_array(bytes)

    def _read_binary(self, code, length=None):
        chunks = []

        while True:
            if b'\x20' <= code <= b'\x2F':
                # binary data length 0-16
                length = ord(code) - 0x20
            elif b'\x34' <= code <= b'\x37':
                # binary data length 0-1023
                len_b1 = (ord(code) - 0x34) << 8
                len_b0 = ord(self._read(1))
                length = len_b0 + len_b1
            else:
                len_bytes = self._read(2)
                length = unpack('>H', len_bytes)[0]
            if length == 0:
                break

            chunks.append(self._read(length))

            if code != b'A':
                break

            length = None
            code = self._read(1)

        return Binary(reduce(operator.add, chunks, b''))

    def _read_map(self, code=None):
        if code is None:
            code = self._read(1)

        if code == b't':
            type_len = unpack('>H', self._read(2))[0]
            if type_len > 0:
                # a typed map deserializes to an object
                result = cls_factory(self._read(type_len))()
            else:
                result = {}

            code = self._read(1)
        else:
            # untyped maps deserialize to a dict
            result = {}
            if code == b'M':
                # Read and discard type
                try:
                    self._read_object()
                except ListMapTerminator:
                    code = b'Z'
                code = self._read(1)

        self._refs.append(result)

        fields = {}

        while code not in (b'z', b'Z'):
            key, value = self._read_keyval(code)

            if key == {}:
                return result

            if isinstance(result, Object):
                fields[str(key)] = value
            else:
                fields[key] = value

            code = self._read(1)

        if isinstance(result, Object):
            result.__setstate__(fields)
        else:
            result.update(fields)

        return result

    def _read_keyval(self, first=None):
        key = self._read_object(first or self._read(1))
        code = self._read(1)
        value = self._read_object(code)

        return key, value

    def _read_fault(self):
        fault = self._read_object()
        return Fault(fault['code'], fault['message'], fault.get('detail'))
