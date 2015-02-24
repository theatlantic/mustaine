import datetime
from struct import unpack

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from mustaine.protocol import (
    Call, Reply, Fault, Binary, Remote, Object, cls_factory)


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
        if isinstance(string, unicode):
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

            if code == 'H' and not self.version:
                if self._result:
                    raise ParseError('Encountered duplicate type header')
                self.read_version()

            elif code == 'R':
                self._result = Reply(version=self.version)

            elif self.version == 1 and code == 'c':
                if self._result:
                    raise ParseError('Encountered duplicate type header')
                self.read_version()
                self._result = Call(version=self.version)

            elif not self._result and code == 'r':
                self.read_version()
                self._result = Reply(version=self.version)

            else:
                if not self._result:
                    raise ParseError("Invalid Hessian message marker: %r" % (code,))

                if self.version == 1 and code == 'H':
                    key, value = self._read_keyval()
                    self._result.headers[key] = value

                elif self.version == 1 and code == 'm':
                    if not isinstance(self._result, Call):
                        raise ParseError('Encountered illegal method name within reply')

                    if self._result.method:
                        raise ParseError('Encountered duplicate method name definition')

                    self._result.method = self._read(unpack('>H', self._read(2))[0])
                    continue

                elif self.version == 1 and code == 'f':
                    if not isinstance(self._result, Reply):
                        raise ParseError('Encountered illegal fault within call')

                    if self._result.value:
                        raise ParseError('Encountered illegal extra object within reply')

                    self._result.value = self._adapter._read_fault()
                    break

                elif self.version == 1 and code == 'z':
                    break

                else:
                    if isinstance(self._result, Call):
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
        self._refs   = []

    def _read(self, n):
        return self._base_parser._read(n)

    def _read_object(self, code=None):
        if code is None:
            code = self._read(1)
        if   code == 'N':
            return None
        elif code == 'T':
            return True
        elif code == 'F':
            return False
        elif code == 'I':
            return int(unpack('>l', self._read(4))[0])
        elif code == 'L':
            return long(unpack('>q', self._read(8))[0])
        elif code == 'D':
            return float(unpack('>d', self._read(8))[0])
        elif code == 'd':
            return self._read_date()
        elif code == 's' or code == 'x':
            fragment = self._read_string()
            next     = self._read(1)
            if next.lower() == code:
                return fragment + self._read_object(next)
            else:
                raise ParseError("Expected terminal string segment, got %r" % (next,))
        elif code == 'S' or code == 'X':
            return self._read_string()
        elif code == 'b':
            fragment = self._read_binary()
            next     = self._read(1)
            if next.lower() == code:
                return fragment + self._read_object(next)
            else:
                raise ParseError("Expected terminal binary segment, got %r" % (next,))
        elif code == 'B':
            return self._read_binary()
        elif code == 'r':
            return self._read_remote()
        elif code == 'R':
            return self._refs[unpack(">L", self._read(4))[0]]
        elif code == 'V':
            return self._read_list()
        elif code == 'M':
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

        return ''.join(bytes).decode('utf-8')

    def _read_binary(self, len=None):
        if len is None:
            len = unpack('>H', self._read(2))[0]
        if len == 0:
            return Binary("")
        return Binary(self._read(len))

    def _read_remote(self):
        r    = Remote()
        code = self._read(1)

        if code == 't':
            r.type = self._read(unpack('>H', self._read(2))[0])
            code   = self._read(1)
        else:
            r.type = None

        if code != 's' and code != 'S':
            raise ParseError("Expected string object while parsing Remote object URL")

        r.url = self._read_object(code)
        return r

    def _read_list(self, code=None):
        if code is None:
            code = self._read(1)

        if code == 't':
            # read and discard list type
            self._read(unpack('>H', self._read(2))[0])
            code = self._read(1)

        if code == 'l':
            # read and discard list length
            self._read(4)
            code = self._read(1)

        result = []
        self._refs.append(result)

        while code != 'z':
            result.append(self._read_object(code))
            code = self._read(1)

        return result

    def _read_map(self):
        code = self._read(1)

        if code == 't':
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
        while code != 'z':
            key, value  = self._read_keyval(code)

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
        key   = self._read_object(first or self._read(1))
        value = self._read_object(self._read(1))

        return key, value


class ParserV2(ParserV1):
    """
    Implementation of Hessian 2.0 Serialization Protocol
        see: http://hessian.caucho.com/doc/hessian-serialization.html
    """

    version = 2

    def _read_object(self, code=None):
        if code is None:
            code = self._read(1)

        if '\x00' <= code <= '\x1F':
            # utf-8 string length 0-32
            return self._read_compact_string(code)
        elif '\x20' <= code <= '\x2F':
            # binary data length 0-16
            # length = ord(code) - 0x20
            return self._read_binary(code)
        elif '\x30' <= code <= '\x33':
            # utf-8 string length 0-1023
            return self._read_compact_string(code)
        elif '\x34' <= code <= '\x37':
            # binary data length 0-1023
            # len_b1 = (ord(code) - 0x34) << 8
            # len_b0 = ord(self._read(1))
            # length = len_b0 + len_b1
            return self._read_binary(code)
        elif '\x38' <= code <= '\x3F':
            # three-octet compact long (-x40000 to x3ffff)
            b2 = (ord(code) - 0x3c) << 16
            b1 = ord(self._read(1)) << 8
            b0 = ord(self._read(1))
            return long(b0 + b1 + b2)
        elif code in ('\x41', '\x42'):
            # 8-bit binary data non-final chunk ('A')
            # 8-bit binary data final chunk ('B')
            return self._read_binary(code)
        elif code == '\x43':
            # object type definition ('C')
            self._read_class_def()
            return self._read_object()
        elif code == '\x48':
            # untyped map ('H')
            return self._read_map()
        elif code == '\x4A':
            # 64-bit UTC millisecond date ('J')
            return self._read_date()
        elif code == '\x4B':
            # 32-bit UTC minute date ('K')
            return self._read_compact_date()
        elif code == '\x4D':
            # map with type ('M')
            return self._read_map(code)
        elif code == '\x4F':
            # object instance ('O')
            return self._read_class_object(code)
        elif code == '\x51':
            # reference to map/list/object - integer ('Q')
            return self._refs[self._read_object()]
        elif code in ('\x52', '\x53'):
            # utf-8 string non-final chunk ('R')
            # utf-8 string final chunk ('S')
            b1 = ord(self._read(1)) << 8
            b0 = ord(self._read(1))
            return self._read_v2_string(code, b0 + b1)
        elif code == '\x55':
            # variable-length list/vector ('U')
            return self._read_list(typed=True, fixed_length=False)
        elif code == '\x56':
            # fixed-length list/vector ('V')
            return self._read_list(typed=True, fixed_length=True)
        elif code == '\x57':
            # variable-length untyped list/vector ('W')
            return self._read_list(typed=False, fixed_length=False)
        elif code == '\x58':
            # fixed-length untyped list/vector ('X')
            return self._read_list(typed=False, fixed_length=True)
        elif code == '\x59':
            # long encoded as 32-bit int ('Y')
            return long(unpack('>l', self._read(4))[0])
        elif code == '\x5A':
            # list/map terminator ('Z')
            raise ListMapTerminator()
        elif code == '\x5B':
            # double 0.0
            return 0.0
        elif code == '\x5C':
            # double 1.0
            return 1.0
        elif code == '\x5D':
            # double byte
            return float(unpack('>b', self._read(1))[0])
        elif code == '\x5E':
            # double short
            return float(unpack('>h', self._read(2))[0])
        elif code == '\x5F':
            # double represented as float
            return float(unpack('>l', self._read(4))[0] / 1000.0)
        elif '\x60' <= code <= '\x6F':
            # object with direct type
            return self._read_class_object(code)
        elif '\x70' <= code <= '\x77':
            # fixed list with direct length
            list_len = ord(code) - 0x70
            return self._read_list(typed=True, fixed_length=True, length=list_len)
        elif '\x78' <= code <= '\x7F':
            # fixed untyped list with direct length
             list_len = ord(code) - 0x78
             return self._read_list(typed=False, fixed_length=True, length=list_len)
        elif '\x80' <= code <= '\xBF':
            # one-octet compact int (-x10 to x3f, x90 is 0)
            return ord(code) - 0x90
        elif '\xC0' <= code <= '\xCF':
            # two-octet compact int (-x800 to x7ff)
            return 256 * (ord(code) - 0xc8) + int(unpack('>B', self._read(1))[0])
        elif '\xD0' <= code <= '\xD7':
            # three-octet compact int (-x40000 to x3ffff)
            b1 = int(unpack('>B', self._read(1))[0])
            b0 = int(unpack('>B', self._read(1))[0])
            return 65536 * (ord(code) - 0xd4) + 256 * b1 + b0
        elif '\xD8' <= code <= '\xEF':
            # one-octet compact long (-x8 to xf, xe0 is 0)
            return long(ord(code) - 0xe0)
        elif '\xF0' <= code <= '\xFF':
            # two-octet compact long (-x800 to x7ff, xf8 is 0)
            b1 = (ord(code) - 0xF8) << 8
            b0 = ord(self._read(1))
            return long(b0 + b1)
        else:
            return super(ParserV2, self)._read_object(code)

    def _read_list(self, typed=False, fixed_length=False, length=None):
        if length is 0:
            return tuple([]) if fixed_length else []

        code = self._read(1)

        if code in ('t', 'l'):
            # Hessian 1.0 list
            return super(ParserV2, self)._read_list(code=code)

        if typed:
            # read and discard list type
            self._read_object(code)
            code = None

        result = []
        self._refs.append(result)

        if fixed_length:
            if length is None:
                length = self._read_object(code)
                code = None
            while len(result) < length:
                result.append(self._read_object(code))
                code = None
        else:
            obj = self._read_object(code)
            code = None
            while obj != 'Z':
                result.append(obj)
                obj = self._read_object()

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
                if '\x00' <= char <= '\x79':
                    chars.append(char)
                elif '\xC2' <= char <= '\xDF':
                    chars.append(char + self._read(1))
                elif '\xE0' <= char <= '\xEF':
                    chars.append(char + self._read(2))
                elif '\xF0' <= char <= '\xF4':
                    chars.append(char + self._read(3))
                length -= 1

            chunks.append(''.join(chars).decode('utf-8'))
            length = None
            if code == 'S':
                break
            try:
                code = self._read(1)
            except ParseError:
                break
        return ''.join(chunks)

    def _read_class_def(self):
        type_name = self._read_object()
        num_fields = self._read_object()
        fields = []
        for i in xrange(0, num_fields):
            fields.append(self._read_object())
        self._classdefs.append(cls_factory(type_name, fields))

    def _read_class_object(self, code):
        if code == 'O':
            classdef_num = self._read_object()
        else:
            classdef_num = ord(code) - 0x60
        classdef = self._classdefs[classdef_num]
        result = classdef()
        self._refs.append(result)
        field_vals = {}
        for f in classdef._mustaine_field_names:
            field_vals[f] = self._read_object()
        result.__setstate__(field_vals)
        return result

    def _read_compact_date(self):
        minutes = unpack('>l', self._read(4))[0]
        return datetime.datetime.utcfromtimestamp(minutes * 60)

    def _read_compact_string(self, code):
        if code >= '\x30':
            len_bytes = chr(ord(code) - 0x30) + self._read(1)
        else:
            len_bytes = '\x00' + code
        length = unpack('>H', len_bytes)[0]

        bytes = []
        while length > 0:
            byte = self._read(1)
            if '\x00' <= byte <= '\x7F':
                bytes.append(byte)
            elif '\xC2' <= byte <= '\xDF':
                bytes.append(byte + self._read(1))
            elif '\xE0' <= byte <= '\xEF':
                bytes.append(byte + self._read(2))
            elif '\xF0' <= byte <= '\xF4':
                bytes.append(byte + self._read(3))
            length -= 1

        return ''.join(bytes).decode('utf-8')

    def _read_binary(self, code, length=None):
        if '\x20' <= code <= '\x2F':
              # binary data length 0-16
              length = ord(code) - 0x20
        elif '\x34' <= code <= '\x37':
              # binary data length 0-1023
              len_b1 = (ord(code) - 0x34) << 8
              len_b0 = ord(self._read(1))
              length = len_b0 + len_b1

        chunks = []

        while True:
            if length is None:
                len_bytes = self._read(2)
                length = unpack('>H', len_bytes)[0]
            if length == 0:
                break

            chunks.append(self._read(length))

            if code != 'A':
                break

            length = None
            code = self._read(1)

        return Binary(''.join(chunks))

    def _read_map(self, code=None):
        if code is None:
            code = self._read(1)

        if code == 't':
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
            if code == 'M':
                # Read and discard type
                try:
                    self._read_object()
                except ListMapTerminator:
                    code = 'Z'
                code = self._read(1)

        self._refs.append(result)

        fields = {}

        while code not in ('z', 'Z'):
            key, value  = self._read_keyval(code)

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
        key   = self._read_object(first or self._read(1))
        code = self._read(1)
        value = self._read_object(code)

        return key, value
