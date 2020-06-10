import warnings

import pytest

from pyhessian import protocol
from pyhessian.client import HessianProxy

from .helpers import ServletProcessWrapper, SUPPORT_DIR


@pytest.fixture(autouse=True)
def raise_warnings_as_exceptions():
    warnings.simplefilter("error", Warning)


@pytest.fixture
def support_dir():
    return SUPPORT_DIR


@pytest.fixture(scope='session', autouse=True)
def servlet_process():
    return ServletProcessWrapper()


@pytest.fixture
def hessian_auth_client(servlet_process):
    client = HessianProxy(servlet_process.http_auth_url, version=1)
    yield client
    if getattr(client, '_client', None):
        client._client.close()


def test_client_http_auth(hessian_auth_client):
    expected = protocol.Binary(b"")
    reply = hessian_auth_client.replyBinary_0()
    assert expected == reply
