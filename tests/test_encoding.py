import datetime

import six

from pyhessian import protocol
from pyhessian.data_types import long
from .base import HessianTestCase

# Caucho's Hessian 2.0 reference service
# interface: http://caucho.com/resin-javadoc/com/caucho/hessian/test/TestHessian2.html


class EncoderTestCase(HessianTestCase):

    def test_encode_binary_0(self):
        arg = protocol.Binary(b"")
        response = self.client.argBinary_0(arg)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_binary_1(self):
        arg = protocol.Binary(b"0")
        response = self.client.argBinary_1(arg)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def get_arg_str_1024(self):
        arg_str = ""
        for i in range(0, 16):
            arg_str += "%d%d%s" % (
                i // 10, i % 10, " 456789012345678901234567890123456789012345678901234567890123\n")
        return arg_str[:1024]

    def get_arg_str_65536(self):
        arg_str = ""
        for i in range(0, 64 * 16):
            arg_str += "%d%d%d%s" % (
                i // 100, (i // 10) % 10, i % 10, " 56789012345678901234567890123456789012345678901234567890123\n")
        return arg_str[:65536]

    def test_encode_binary_1023(self):
        arg = protocol.Binary(six.b(self.get_arg_str_1024()[:1023]))
        response = self.client.argBinary_1023(arg)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_binary_1024(self):
        arg = protocol.Binary(six.b(self.get_arg_str_1024()[:1024]))
        response = self.client.argBinary_1024(arg)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_binary_15(self):
        response = self.client.argBinary_15(protocol.Binary(b"012345678901234"))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_binary_16(self):
        response = self.client.argBinary_16(protocol.Binary(b"0123456789012345"))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_binary_65536(self):
        arg = protocol.Binary(six.b(self.get_arg_str_65536()))
        response = self.client.argBinary_65536(arg)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_date_0(self):
        arg = datetime.datetime.utcfromtimestamp(0)
        response = self.client.argDate_0(arg)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_date_1(self):
        response = self.client.argDate_1(datetime.datetime(1998, 5, 8, 9, 51, 31))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_date_2(self):
        response = self.client.argDate_2(datetime.datetime(1998, 5, 8, 9, 51, 0))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_0_0(self):
        response = self.client.argDouble_0_0(0.0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_0_001(self):
        response = self.client.argDouble_0_001(0.001)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_1_0(self):
        response = self.client.argDouble_1_0(1.0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_127_0(self):
        response = self.client.argDouble_127_0(127.0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_128_0(self):
        response = self.client.argDouble_128_0(128.0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_2_0(self):
        response = self.client.argDouble_2_0(2.0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_3_14159(self):
        response = self.client.argDouble_3_14159(3.14159)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_32767_0(self):
        response = self.client.argDouble_32767_0(32767.0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_65_536(self):
        response = self.client.argDouble_65_536(65.536)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_m0_001(self):
        response = self.client.argDouble_m0_001(-0.001)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_m128_0(self):
        response = self.client.argDouble_m128_0(-128.0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_m129_0(self):
        response = self.client.argDouble_m129_0(-129.0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_double_m32768_0(self):
        response = self.client.argDouble_m32768_0(-32768.0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_false(self):
        result = self.client.argFalse(False)
        self.assertEqual(True, result, result)

    def test_encode_int_0(self):
        response = self.client.argInt_0(0)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_0x30(self):
        response = self.client.argInt_0x30(0x30)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_0x3ffff(self):
        response = self.client.argInt_0x3ffff(0x3ffff)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_0x40000(self):
        response = self.client.argInt_0x40000(0x40000)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_0x7ff(self):
        response = self.client.argInt_0x7ff(0x7ff)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_0x7fffffff(self):
        response = self.client.argInt_0x7fffffff(0x7fffffff)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_0x800(self):
        response = self.client.argInt_0x800(0x800)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_1(self):
        response = self.client.argInt_1(1)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_47(self):
        response = self.client.argInt_47(47)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_m0x40000(self):
        response = self.client.argInt_m0x40000(-0x40000)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_m0x40001(self):
        response = self.client.argInt_m0x40001(-0x40001)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_m0x800(self):
        response = self.client.argInt_m0x800(-0x800)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_m0x80000000(self):
        response = self.client.argInt_m0x80000000(-0x80000000)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_m0x801(self):
        response = self.client.argInt_m0x801(-0x801)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_m16(self):
        response = self.client.argInt_m16(-16)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_int_m17(self):
        response = self.client.argInt_m17(-17)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_0(self):
        response = self.client.argLong_0(long(0))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_0x10(self):
        response = self.client.argLong_0x10(long(0x10))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_0x3ffff(self):
        response = self.client.argLong_0x3ffff(long(0x3ffff))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_0x40000(self):
        response = self.client.argLong_0x40000(long(0x40000))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_0x7ff(self):
        response = self.client.argLong_0x7ff(long(0x7ff))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_0x7fffffff(self):
        response = self.client.argLong_0x7fffffff(long(0x7fffffff))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_0x800(self):
        response = self.client.argLong_0x800(long(0x800))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_0x80000000(self):
        response = self.client.argLong_0x80000000(long(0x80000000))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_1(self):
        response = self.client.argLong_1(long(1))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_15(self):
        response = self.client.argLong_15(long(15))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_m0x40000(self):
        response = self.client.argLong_m0x40000(long(-0x40000))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_m0x40001(self):
        response = self.client.argLong_m0x40001(long(-0x40001))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_m0x800(self):
        response = self.client.argLong_m0x800(long(-0x800))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_m0x80000000(self):
        response = self.client.argLong_m0x80000000(long(-0x80000000))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_m0x80000001(self):
        response = self.client.argLong_m0x80000001(long(-0x80000001))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_m0x801(self):
        response = self.client.argLong_m0x801(long(-0x801))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_m8(self):
        response = self.client.argLong_m8(long(-8))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_long_m9(self):
        response = self.client.argLong_m9(long(-9))
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_null(self):
        response = self.client.argNull(None)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_object_0(self):
        payload = protocol.object_factory('com.caucho.hessian.test.A0')
        response = self.client.argObject_0(payload)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_object_1(self):
        payload = protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0)

        response = self.client.argObject_1(payload)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_object_16(self):
        payload = [
            protocol.object_factory('com.caucho.hessian.test.A0'),
            protocol.object_factory('com.caucho.hessian.test.A1'),
            protocol.object_factory('com.caucho.hessian.test.A2'),
            protocol.object_factory('com.caucho.hessian.test.A3'),
            protocol.object_factory('com.caucho.hessian.test.A4'),
            protocol.object_factory('com.caucho.hessian.test.A5'),
            protocol.object_factory('com.caucho.hessian.test.A6'),
            protocol.object_factory('com.caucho.hessian.test.A7'),
            protocol.object_factory('com.caucho.hessian.test.A8'),
            protocol.object_factory('com.caucho.hessian.test.A9'),
            protocol.object_factory('com.caucho.hessian.test.A10'),
            protocol.object_factory('com.caucho.hessian.test.A11'),
            protocol.object_factory('com.caucho.hessian.test.A12'),
            protocol.object_factory('com.caucho.hessian.test.A13'),
            protocol.object_factory('com.caucho.hessian.test.A14'),
            protocol.object_factory('com.caucho.hessian.test.A15'),
            protocol.object_factory('com.caucho.hessian.test.A16'),
        ]

        response = self.client.argObject_16(payload)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_object_2(self):
        payload = [
            protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0),
            protocol.object_factory('com.caucho.hessian.test.TestObject', _value=1),
        ]

        response = self.client.argObject_2(payload)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_object_2a(self):
        payload = protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0)

        response = self.client.argObject_2a([payload, payload])
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_object_2b(self):
        payload = [
            protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0),
            protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0),
        ]

        response = self.client.argObject_2b(payload)
        self.assertEqual(response, True, "Debug response: %s" % response)

    ### argObject_3 causes a stack pop. BOOM, recursion.
    def test_encode_object_3(self):
        payload = protocol.object_factory('com.caucho.hessian.test.TestCons', _first='a', _rest=None)
        payload._rest = payload

        response = self.client.argObject_3(payload)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_string_0(self):
        response = self.client.argString_0("")
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_string_1(self):
        response = self.client.argString_1("0")
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_string_31(self):
        payload = "0123456789012345678901234567890"
        response = self.client.argString_31(payload)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_string_32(self):
        payload = "01234567890123456789012345678901"
        response = self.client.argString_32(payload)
        self.assertEqual(response, True, "Debug response: %s" % response)

    ### here, we have to generate big convoluted strings. later.
    def test_encode_string_1023(self):
        arg = self.get_arg_str_1024()[:1023]
        response = self.client.argString_1023(arg)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_string_1024(self):
        response = self.client.argString_1024(self.get_arg_str_1024())
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_string_65536(self):
        response = self.client.argString_65536(self.get_arg_str_65536())
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_true(self):
        response = self.client.argTrue(True)
        self.assertEqual(response, True, "Debug response: %s" % response)

    def test_encode_string_emoji(self):
        response = self.client.argString_emoji(u"\U0001F603")
        self.assertTrue(response, "Debug response: %s" % response)
