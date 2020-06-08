# Caucho's Hessian 2.0 reference service
# interface: http://caucho.com/resin-javadoc/com/caucho/hessian/test/TestHessian2.html
import datetime

import six

import pytest

from pyhessian import protocol
from pyhessian.parser import Parser
from pyhessian.data_types import long


@pytest.fixture
def client_v1(hessian_client_v2):
    yield hessian_client_v2


@pytest.fixture
def client_v2(hessian_client_v2):
    yield hessian_client_v2


@pytest.fixture(params=['v1', 'v2'])
def client(request, client_v1, client_v2):
    if request.param == 'v1':
        yield client_v1
    else:
        yield client_v2


def test_parse_binary_0(client):
    expected = protocol.Binary(b"")
    reply = client.replyBinary_0()
    assert reply == expected


def test_parse_binary_1(client):
    expected = protocol.Binary(b"0")
    reply = client.replyBinary_1()
    assert reply == expected


def test_parse_binary_1023(client, str_1024):
    expected = protocol.Binary(six.b(str_1024[:1023]))
    reply = client.replyBinary_1023()
    assert reply == expected


def test_parse_binary_1024(client, str_1024):
    expected = protocol.Binary(six.b(str_1024[:1024]))
    reply = client.replyBinary_1024()
    assert reply == expected


def test_parse_binary_15(client):
    assert client.replyBinary_15() == protocol.Binary(b"012345678901234")


def test_parse_binary_16(client):
    assert client.replyBinary_16() == protocol.Binary(b"0123456789012345")


def test_parse_binary_65536(client, str_65536):
    expected = protocol.Binary(six.b(str_65536))
    reply = client.replyBinary_65536()
    assert reply == expected


def test_parse_date_0(client):
    expected = datetime.datetime.utcfromtimestamp(0)
    reply = client.replyDate_0()
    assert reply == expected


def test_parse_date_1(client):
    expected = datetime.datetime(1998, 5, 8, 9, 51, 31)
    reply = client.replyDate_1()
    assert reply == expected


def test_parse_date_2(client):
    expected = datetime.datetime(1998, 5, 8, 9, 51, 0)
    reply = client.replyDate_2()
    assert reply == expected


def test_parse_double_0_0(client):
    assert client.replyDouble_0_0() == 0.0


def test_parse_double_0_001(client):
    expected = 0.001
    reply = client.replyDouble_0_001()
    assert reply == expected


def test_parse_double_1_0(client):
    expected = 1.0
    reply = client.replyDouble_1_0()
    assert reply == expected


def test_parse_double_127_0(client):
    expected = 127.0
    reply = client.replyDouble_127_0()
    assert reply == expected


def test_parse_double_128_0(client):
    expected = 128.0
    reply = client.replyDouble_128_0()
    assert reply == expected


def test_parse_double_2_0(client):
    expected = 2.0
    reply = client.replyDouble_2_0()
    assert reply == expected


def test_parse_double_3_14159(client):
    expected = 3.14159
    reply = client.replyDouble_3_14159()
    assert reply == expected


def test_parse_double_32767_0(client):
    expected = 32767.0
    reply = client.replyDouble_32767_0()
    assert reply == expected


def test_parse_double_65_536(client):
    expected = 65.536
    reply = client.replyDouble_65_536()
    assert reply == expected


def test_parse_double_m0_001(client):
    expected = -0.001
    reply = client.replyDouble_m0_001()
    assert reply == expected


def test_parse_double_m128_0(client):
    expected = -128.0
    reply = client.replyDouble_m128_0()
    assert reply == expected


def test_parse_double_m129_0(client):
    expected = -129.0
    reply = client.replyDouble_m129_0()
    assert reply == expected


def test_parse_double_m32768_0(client):
    expected = -32768.0
    reply = client.replyDouble_m32768_0()
    assert reply == expected


def test_parse_false(client):
    expected = False
    reply = client.replyFalse()
    assert reply == expected


def test_parse_int_0(client):
    expected = 0
    reply = client.replyInt_0()
    assert reply == expected


def test_parse_int_0x30(client):
    expected = 0x30
    reply = client.replyInt_0x30()
    assert reply == expected


def test_parse_int_0x3ffff(client):
    expected = 0x3ffff
    reply = client.replyInt_0x3ffff()
    assert reply == expected


def test_parse_int_0x40000(client):
    expected = 0x40000
    reply = client.replyInt_0x40000()
    assert reply == expected


def test_parse_int_0x7ff(client):
    expected = 0x7ff
    reply = client.replyInt_0x7ff()
    assert reply == expected


def test_parse_int_0x7fffffff(client):
    expected = 0x7fffffff
    reply = client.replyInt_0x7fffffff()
    assert reply == expected


def test_parse_int_0x800(client):
    expected = 0x800
    reply = client.replyInt_0x800()
    assert reply == expected


def test_parse_int_1(client):
    expected = 1
    reply = client.replyInt_1()
    assert reply == expected


def test_parse_int_47(client):
    expected = 47
    reply = client.replyInt_47()
    assert reply == expected


def test_parse_int_m0x40000(client):
    expected = -0x40000
    reply = client.replyInt_m0x40000()
    assert reply == expected


def test_parse_int_m0x40001(client):
    expected = -0x40001
    reply = client.replyInt_m0x40001()
    assert reply == expected


def test_parse_int_m0x800(client):
    expected = -0x800
    reply = client.replyInt_m0x800()
    assert reply == expected


def test_parse_int_m0x80000000(client):
    expected = -0x80000000
    reply = client.replyInt_m0x80000000()
    assert reply == expected


def test_parse_int_m0x801(client):
    expected = -0x801
    reply = client.replyInt_m0x801()
    assert reply == expected


def test_parse_int_m16(client):
    expected = -16
    reply = client.replyInt_m16()
    assert reply == expected


def test_parse_int_m17(client):
    expected = -17
    reply = client.replyInt_m17()
    assert reply == expected


def test_parse_long_0(client):
    expected = long(0)
    reply = client.replyLong_0()
    assert reply == expected


def test_parse_long_0x10(client):
    expected = long(0x10)
    reply = client.replyLong_0x10()
    assert reply == expected


def test_parse_long_0x3ffff(client):
    expected = long(0x3ffff)
    reply = client.replyLong_0x3ffff()
    assert reply == expected


def test_parse_long_0x40000(client):
    expected = long(0x40000)
    reply = client.replyLong_0x40000()
    assert reply == expected


def test_parse_long_0x7ff(client):
    expected = long(0x7ff)
    reply = client.replyLong_0x7ff()
    assert reply == expected


def test_parse_long_0x7fffffff(client):
    expected = long(0x7fffffff)
    reply = client.replyLong_0x7fffffff()
    assert reply == expected


def test_parse_long_0x800(client):
    expected = long(0x800)
    reply = client.replyLong_0x800()
    assert reply == expected


def test_parse_long_0x80000000(client):
    expected = long(0x80000000)
    reply = client.replyLong_0x80000000()
    assert reply == expected


def test_parse_long_1(client):
    expected = long(1)
    reply = client.replyLong_1()
    assert reply == expected


def test_parse_long_15(client):
    expected = long(15)
    reply = client.replyLong_15()
    assert reply == expected


def test_parse_long_m0x40000(client):
    expected = long(-0x40000)
    reply = client.replyLong_m0x40000()
    assert reply == expected


def test_parse_long_m0x40001(client):
    expected = long(-0x40001)
    reply = client.replyLong_m0x40001()
    assert reply == expected


def test_parse_long_m0x800(client):
    expected = long(-0x800)
    reply = client.replyLong_m0x800()
    assert reply == expected


def test_parse_long_m0x80000000(client):
    expected = long(-0x80000000)
    reply = client.replyLong_m0x80000000()
    assert reply == expected


def test_parse_long_m0x80000001(client):
    expected = long(-0x80000001)
    reply = client.replyLong_m0x80000001()
    assert reply == expected


def test_parse_long_m0x801(client):
    expected = long(-0x801)
    reply = client.replyLong_m0x801()
    assert reply == expected


def test_parse_long_m8(client):
    expected = long(-8)
    reply = client.replyLong_m8()
    assert reply == expected


def test_parse_long_m9(client):
    expected = long(-9)
    reply = client.replyLong_m9()
    assert reply == expected


def test_parse_null(client):
    expected = None
    reply = client.replyNull()
    assert reply == expected


def test_parse_object_0(client):
    expected = protocol.object_factory('com.caucho.hessian.test.A0')
    reply = client.replyObject_0()
    assert reply == expected


def test_parse_object_1(client):
    expected = protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0)
    reply = client.replyObject_1()
    assert reply == expected


def test_parse_object_16(client):
    expected = (
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
    )
    reply = client.replyObject_16()
    assert reply == expected


def test_parse_object_2(client):
    expected = (
        protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0),
        protocol.object_factory('com.caucho.hessian.test.TestObject', _value=1),
    )
    reply = client.replyObject_2()
    assert reply == expected


def test_parse_object_2a(client):
    payload = protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0)
    expected = (payload, payload)
    reply = client.replyObject_2a()
    assert reply == expected


def test_parse_object_2b(client):
    expected = (
        protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0),
        protocol.object_factory('com.caucho.hessian.test.TestObject', _value=0),
    )
    reply = client.replyObject_2b()
    assert reply == expected


def test_parse_object_3(client):
    expected = protocol.object_factory('com.caucho.hessian.test.TestCons', _first='a', _rest=None)
    expected._rest = expected
    reply = client.replyObject_3()
    assert reply == expected


def test_parse_string_0(client):
    expected = ""
    reply = client.replyString_0()
    assert reply == expected


def test_parse_string_1(client):
    expected = "0"
    reply = client.replyString_1()
    assert reply == expected


def test_parse_string_31(client):
    expected = "0123456789012345678901234567890"
    assert client.replyString_31() == expected


def test_parse_string_32(client):
    expected = "01234567890123456789012345678901"
    assert client.replyString_32() == expected


def test_parse_string_1023(client, str_1024):
    assert client.replyString_1023() == str_1024[:1023]


def test_parse_string_1024(client, str_1024):
    assert client.replyString_1024() == str_1024


def test_parse_string_65536(client, str_65536):
    assert client.replyString_65536() == str_65536


def test_parse_true(client):
    assert client.replyTrue() is True


def test_parse_untyped_fixed_list_0(client):
    expected = tuple([])
    reply = client.replyUntypedFixedList_0()
    assert reply == expected


def test_parse_untyped_fixed_list_1(client):
    expected = ("1", )
    reply = client.replyUntypedFixedList_1()
    assert reply == expected


def test_parse_untyped_fixed_list_7(client):
    expected = ("1", "2", "3", "4", "5", "6", "7")
    reply = client.replyUntypedFixedList_7()
    assert reply == expected


def test_parse_untyped_fixed_list_8(client):
    expected = ("1", "2", "3", "4", "5", "6", "7", "8")
    reply = client.replyUntypedFixedList_8()
    assert reply == expected


def test_parse_typed_fixed_list_0(client):
    expected = tuple([])
    reply = client.replyTypedFixedList_0()
    assert reply == expected


def test_parse_typed_fixed_list_1(client):
    expected = ("1", )
    reply = client.replyTypedFixedList_1()
    assert reply == expected


def test_parse_typed_fixed_list_7(client):
    expected = ("1", "2", "3", "4", "5", "6", "7")
    reply = client.replyTypedFixedList_7()
    assert reply == expected


def test_parse_typed_fixed_list_8(client):
    expected = ("1", "2", "3", "4", "5", "6", "7", "8")
    reply = client.replyTypedFixedList_8()
    assert reply == expected


def test_parse_untyped_map_0(client):
    expected = {}
    reply = client.replyUntypedMap_0()
    assert reply == expected


def test_parse_untyped_map_1(client):
    expected = {"a": 0}
    reply = client.replyUntypedMap_1()
    assert reply == expected


def test_parse_untyped_map_2(client):
    expected = {0: "a", 1: "b"}
    reply = client.replyUntypedMap_2()
    assert reply == expected


def test_parse_untyped_map_3(client):
    reply = client.replyUntypedMap_3()
    expected = {('a', ): 0}
    assert reply == expected


def test_fault_method_does_not_exist(client):
    with pytest.raises(protocol.Fault):
        client.nonExistantMethod()


def test_parse_string_emoji(client):
    expected = u"\U0001F603".encode('utf-8')
    reply = client.replyString_emoji().encode('utf-8')
    assert reply == expected


def test_parse_v1_call(client_v1):
    expected = protocol.Call(method=b'methodNull', args=[], version=1)
    encoded = b'c\x01\x00m\x00\nmethodNullz'
    decoded = Parser().parse_string(encoded)
    assert expected == decoded


def test_parse_v2_typed_map_0(client_v2):
    expected = {}
    reply = client_v2.replyTypedMap_0()
    assert reply == expected


def test_parse_v2_typed_map_1(client_v2):
    expected = {"a": 0}
    reply = client_v2.replyTypedMap_1()
    assert reply == expected


def test_parse_v2_typed_map_2(client_v2):
    expected = {0: "a", 1: "b"}
    reply = client_v2.replyTypedMap_2()
    assert reply == expected


def test_parse_v2_typed_map_3(client_v2):
    reply = client_v2.replyTypedMap_3()
    expected = {('a', ): 0}
    assert reply == expected


def test_parse_v2_call(client_v2):
    expected = protocol.Call(method=b'methodNull', args=[], version=2)
    encoded = b'H\x02\x00C\x0amethodNull\x90'
    decoded = Parser().parse_string(encoded)
    assert expected == decoded


def test_parse_v2_untyped_variable_list_0(client_v2):
    expected = []
    reply = client_v2.replyUntypedVariableList_0()
    assert reply == expected


def test_parse_v2_untyped_variable_list_1(client_v2):
    expected = ['a', 'b']
    reply = client_v2.replyUntypedVariableList_1()
    assert reply == expected
