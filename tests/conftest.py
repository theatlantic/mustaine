import os
import ssl
import warnings

import pytest

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
def hessian_client_v1(servlet_process):
    client = HessianProxy(servlet_process.http_url, version=1)
    yield client
    if getattr(client, '_client', None):
        client._client.close()


@pytest.fixture
def hessian_client_v2(servlet_process):
    client = HessianProxy(servlet_process.http_url, version=2)
    yield client
    if getattr(client, '_client', None):
        client._client.close()


@pytest.fixture
def hessian_client_ssl(servlet_process, support_dir):
    cert_dir = os.path.join(support_dir, 'certs')
    server_crt = os.path.join(cert_dir, 'caroot.crt')
    client_crt = os.path.join(cert_dir, 'client.crt')
    client_key = os.path.join(cert_dir, 'client.key')
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_crt)
    context.load_cert_chain(certfile=client_crt, keyfile=client_key)
    client = HessianProxy(servlet_process.https_url, version=1, context=context)
    yield client
    if getattr(client, '_client', None):
        client._client.close()


@pytest.fixture
def str_1024():
    s = ""
    for i in range(0, 16):
        s += "%d%d%s" % (
            i // 10, i % 10, " 456789012345678901234567890123456789012345678901234567890123\n")
    return s[:1024]


@pytest.fixture
def str_65536():
    s = ""
    for i in range(0, 64 * 16):
        s += "%d%d%d%s" % (
            i // 100, (i // 10) % 10, i % 10, " 56789012345678901234567890123456789012345678901234567890123\n")
    return s[:65536]
