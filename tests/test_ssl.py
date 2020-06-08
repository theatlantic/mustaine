import os
import ssl

from pyhessian import protocol
from pyhessian.client import HessianProxy

from .base import SUPPORT_DIR, HessianTestCase


CERT_DIR = os.path.join(SUPPORT_DIR, 'certs')


class HttpsTestCase(HessianTestCase):

    def setUp(self):
        super(HttpsTestCase, self).setUp()

        server_crt = os.path.join(CERT_DIR, 'caroot.crt')
        client_crt = os.path.join(CERT_DIR, 'client.crt')
        client_key = os.path.join(CERT_DIR, 'client.key')
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_crt)
        context.load_cert_chain(certfile=client_crt, keyfile=client_key)
        self.ssl_client = HessianProxy(
            self.api_url_ssl, version=self.version, context=context)

    def test_ssl_opts(self):
        expected = protocol.Binary(b"")
        reply = self.ssl_client.replyBinary_0()
        self.assertEqual(expected, reply)
