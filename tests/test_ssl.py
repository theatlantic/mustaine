from pyhessian import protocol


def test_ssl_opts(hessian_client_ssl):
    expected = protocol.Binary(b"")
    reply = hessian_client_ssl.replyBinary_0()
    assert expected == reply
