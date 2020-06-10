import datetime

import six

from pyhessian import protocol
from pyhessian.data_types import long

import pytest


@pytest.fixture
def client(hessian_client_v1):
    yield hessian_client_v1


def test_encode_binary_0(client):
    arg = protocol.Binary(b"")
    response = client.argBinary_0(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_binary_1(client):
    arg = protocol.Binary(b"0")
    response = client.argBinary_1(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_binary_1023(client, str_1024):
    arg = protocol.Binary(six.b(str_1024[:1023]))
    response = client.argBinary_1023(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_binary_1024(client, str_1024):
    arg = protocol.Binary(six.b(str_1024[:1024]))
    response = client.argBinary_1024(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_binary_15(client):
    response = client.argBinary_15(protocol.Binary(b"012345678901234"))
    assert response is True, "Debug response: %s" % response


def test_encode_binary_16(client):
    response = client.argBinary_16(protocol.Binary(b"0123456789012345"))
    assert response is True, "Debug response: %s" % response


def test_encode_binary_65536(client, str_65536):
    arg = protocol.Binary(six.b(str_65536))
    response = client.argBinary_65536(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_date_0(client):
    arg = datetime.datetime.utcfromtimestamp(0)
    response = client.argDate_0(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_date_1(client):
    response = client.argDate_1(datetime.datetime(1998, 5, 8, 9, 51, 31))
    assert response is True, "Debug response: %s" % response


def test_encode_date_2(client):
    response = client.argDate_2(datetime.datetime(1998, 5, 8, 9, 51, 0))
    assert response is True, "Debug response: %s" % response


def test_encode_double_0_0(client):
    response = client.argDouble_0_0(0.0)
    assert response is True, "Debug response: %s" % response


def test_encode_double_0_001(client):
    response = client.argDouble_0_001(0.001)
    assert response is True, "Debug response: %s" % response


def test_encode_double_1_0(client):
    response = client.argDouble_1_0(1.0)
    assert response is True, "Debug response: %s" % response


def test_encode_double_127_0(client):
    response = client.argDouble_127_0(127.0)
    assert response is True, "Debug response: %s" % response


def test_encode_double_128_0(client):
    response = client.argDouble_128_0(128.0)
    assert response is True, "Debug response: %s" % response


def test_encode_double_2_0(client):
    response = client.argDouble_2_0(2.0)
    assert response is True, "Debug response: %s" % response


def test_encode_double_3_14159(client):
    response = client.argDouble_3_14159(3.14159)
    assert response is True, "Debug response: %s" % response


def test_encode_double_32767_0(client):
    response = client.argDouble_32767_0(32767.0)
    assert response is True, "Debug response: %s" % response


def test_encode_double_65_536(client):
    response = client.argDouble_65_536(65.536)
    assert response is True, "Debug response: %s" % response


def test_encode_double_m0_001(client):
    response = client.argDouble_m0_001(-0.001)
    assert response is True, "Debug response: %s" % response


def test_encode_double_m128_0(client):
    response = client.argDouble_m128_0(-128.0)
    assert response is True, "Debug response: %s" % response


def test_encode_double_m129_0(client):
    response = client.argDouble_m129_0(-129.0)
    assert response is True, "Debug response: %s" % response


def test_encode_double_m32768_0(client):
    response = client.argDouble_m32768_0(-32768.0)
    assert response is True, "Debug response: %s" % response


def test_encode_false(client):
    response = client.argFalse(False)
    assert response is True, "Debug response: %s" % response


def test_encode_int_0(client):
    response = client.argInt_0(0)
    assert response is True, "Debug response: %s" % response


def test_encode_int_0x30(client):
    response = client.argInt_0x30(0x30)
    assert response is True, "Debug response: %s" % response


def test_encode_int_0x3ffff(client):
    response = client.argInt_0x3ffff(0x3ffff)
    assert response is True, "Debug response: %s" % response


def test_encode_int_0x40000(client):
    response = client.argInt_0x40000(0x40000)
    assert response is True, "Debug response: %s" % response


def test_encode_int_0x7ff(client):
    response = client.argInt_0x7ff(0x7ff)
    assert response is True, "Debug response: %s" % response


def test_encode_int_0x7fffffff(client):
    response = client.argInt_0x7fffffff(0x7fffffff)
    assert response is True, "Debug response: %s" % response


def test_encode_int_0x800(client):
    response = client.argInt_0x800(0x800)
    assert response is True, "Debug response: %s" % response


def test_encode_int_1(client):
    response = client.argInt_1(1)
    assert response is True, "Debug response: %s" % response


def test_encode_int_47(client):
    response = client.argInt_47(47)
    assert response is True, "Debug response: %s" % response


def test_encode_int_m0x40000(client):
    response = client.argInt_m0x40000(-0x40000)
    assert response is True, "Debug response: %s" % response


def test_encode_int_m0x40001(client):
    response = client.argInt_m0x40001(-0x40001)
    assert response is True, "Debug response: %s" % response


def test_encode_int_m0x800(client):
    response = client.argInt_m0x800(-0x800)
    assert response is True, "Debug response: %s" % response


def test_encode_int_m0x80000000(client):
    response = client.argInt_m0x80000000(-0x80000000)
    assert response is True, "Debug response: %s" % response


def test_encode_int_m0x801(client):
    response = client.argInt_m0x801(-0x801)
    assert response is True, "Debug response: %s" % response


def test_encode_int_m16(client):
    response = client.argInt_m16(-16)
    assert response is True, "Debug response: %s" % response


def test_encode_int_m17(client):
    response = client.argInt_m17(-17)
    assert response is True, "Debug response: %s" % response


def test_encode_long_0(client):
    response = client.argLong_0(long(0))
    assert response is True, "Debug response: %s" % response


def test_encode_long_0x10(client):
    response = client.argLong_0x10(long(0x10))
    assert response is True, "Debug response: %s" % response


def test_encode_long_0x3ffff(client):
    response = client.argLong_0x3ffff(long(0x3ffff))
    assert response is True, "Debug response: %s" % response


def test_encode_long_0x40000(client):
    response = client.argLong_0x40000(long(0x40000))
    assert response is True, "Debug response: %s" % response


def test_encode_long_0x7ff(client):
    response = client.argLong_0x7ff(long(0x7ff))
    assert response is True, "Debug response: %s" % response


def test_encode_long_0x7fffffff(client):
    response = client.argLong_0x7fffffff(long(0x7fffffff))
    assert response is True, "Debug response: %s" % response


def test_encode_long_0x800(client):
    response = client.argLong_0x800(long(0x800))
    assert response is True, "Debug response: %s" % response


def test_encode_long_0x80000000(client):
    response = client.argLong_0x80000000(long(0x80000000))
    assert response is True, "Debug response: %s" % response


def test_encode_long_1(client):
    response = client.argLong_1(long(1))
    assert response is True, "Debug response: %s" % response


def test_encode_long_15(client):
    response = client.argLong_15(long(15))
    assert response is True, "Debug response: %s" % response


def test_encode_long_m0x40000(client):
    response = client.argLong_m0x40000(long(-0x40000))
    assert response is True, "Debug response: %s" % response


def test_encode_long_m0x40001(client):
    response = client.argLong_m0x40001(long(-0x40001))
    assert response is True, "Debug response: %s" % response


def test_encode_long_m0x800(client):
    response = client.argLong_m0x800(long(-0x800))
    assert response is True, "Debug response: %s" % response


def test_encode_long_m0x80000000(client):
    response = client.argLong_m0x80000000(long(-0x80000000))
    assert response is True, "Debug response: %s" % response


def test_encode_long_m0x80000001(client):
    response = client.argLong_m0x80000001(long(-0x80000001))
    assert response is True, "Debug response: %s" % response


def test_encode_long_m0x801(client):
    response = client.argLong_m0x801(long(-0x801))
    assert response is True, "Debug response: %s" % response


def test_encode_long_m8(client):
    response = client.argLong_m8(long(-8))
    assert response is True, "Debug response: %s" % response


def test_encode_long_m9(client):
    response = client.argLong_m9(long(-9))
    assert response is True, "Debug response: %s" % response


def test_encode_null(client):
    response = client.argNull(None)
    assert response is True, "Debug response: %s" % response


def test_encode_object_0(client):
    payload = protocol.object_factory('com.caucho.hessian.test.A0')
    response = client.argObject_0(payload)
    assert response is True, "Debug response: %s" % response


def test_encode_object_1(client):
    payload = protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0)

    response = client.argObject_1(payload)
    assert response is True, "Debug response: %s" % response


def test_encode_object_16(client):
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

    response = client.argObject_16(payload)
    assert response is True, "Debug response: %s" % response


def test_encode_object_2(client):
    payload = [
        protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0),
        protocol.object_factory('com.caucho.hessian.test.TestObject', _value=1),
    ]

    response = client.argObject_2(payload)
    assert response is True, "Debug response: %s" % response


def test_encode_object_2a(client):
    payload = protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0)

    response = client.argObject_2a([payload, payload])
    assert response is True, "Debug response: %s" % response


def test_encode_object_2b(client):
    obj = protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0)
    payload = [obj, obj]

    response = client.argObject_2b(payload)
    assert response is True, "Debug response: %s" % response


def test_encode_object_3(client):
    payload = protocol.object_factory('com.caucho.hessian.test.TestCons', _first='a', _rest=None)
    payload._rest = payload

    response = client.argObject_3(payload)
    assert response is True, "Debug response: %s" % response


def test_encode_string_0(client):
    response = client.argString_0("")
    assert response is True, "Debug response: %s" % response


def test_encode_string_1(client):
    response = client.argString_1("0")
    assert response is True, "Debug response: %s" % response


def test_encode_string_31(client):
    payload = "0123456789012345678901234567890"
    response = client.argString_31(payload)
    assert response is True, "Debug response: %s" % response


def test_encode_string_32(client):
    payload = "01234567890123456789012345678901"
    response = client.argString_32(payload)
    assert response is True, "Debug response: %s" % response


def test_encode_string_1023(client, str_1024):
    arg = str_1024[:1023]
    response = client.argString_1023(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_string_1024(client, str_1024):
    response = client.argString_1024(str_1024)
    assert response is True, "Debug response: %s" % response


def test_encode_string_65536(client, str_65536):
    response = client.argString_65536(str_65536)
    assert response is True, "Debug response: %s" % response


def test_encode_true(client):
    response = client.argTrue(True)
    assert response is True, "Debug response: %s" % response


def test_encode_string_emoji(client):
    response = client.argString_emoji(u"\U0001F603")
    assert response is True, "Debug response: %s" % response


def test_encode_compact_string_unicode_two_octets(client):
    arg = u'\xe9'
    response = client.argString_unicodeTwoOctetsCompact(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_compact_string_unicode_three_octets(client):
    arg = u'\u5b57'
    response = client.argString_unicodeThreeOctetsCompact(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_string_unicode_two_octets(client):
    arg = u'\xe9' * 64
    response = client.argString_unicodeTwoOctets(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_string_unicode_three_octets(client):
    arg = u'\u5b57' * 64
    response = client.argString_unicodeThreeOctets(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_list_of_lists_with_ref(client):
    obj = protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0)
    l = (obj, obj)
    arg = (l, l)
    response = client.argListOfListWithRefs(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_untyped_fixed_list_0(client):
    arg = tuple([])
    response = client.argUntypedFixedList_0(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_untyped_fixed_list_1(client):
    arg = ("1", )
    response = client.argUntypedFixedList_1(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_untyped_fixed_list_7(client):
    arg = ("1", "2", "3", "4", "5", "6", "7")
    response = client.argUntypedFixedList_7(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_untyped_fixed_list_8(client):
    arg = ("1", "2", "3", "4", "5", "6", "7", "8")
    response = client.argUntypedFixedList_8(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_untyped_map_0(client):
    arg = {}
    response = client.argUntypedMap_0(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_untyped_map_1(client):
    arg = {"a": 0}
    response = client.argUntypedMap_1(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_untyped_map_2(client):
    arg = {0: "a", 1: "b"}
    response = client.argUntypedMap_2(arg)
    assert response is True, "Debug response: %s" % response


def test_encode_untyped_map_3(client):
    arg = {('a', ): 0}
    response = client.argUntypedMap_3(arg)
    assert response is True, "Debug response: %s" % response
