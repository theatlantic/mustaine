import os
import re
from subprocess import Popen, PIPE
import select
import signal
from threading import Timer

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pyhessian.client import HessianProxy


SUPPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'support'))
TEST_JAR = os.path.join(SUPPORT_DIR, 'hessian-test-servlet.jar')

re_port_number = re.compile(
    r'Listening on http port: (?P<http_port>\d+), '
    r'ssl port: (?P<ssl_port>\d+)$')


class HessianTestCase(unittest.TestCase):

    version = 1
    proc = None
    api_url = None

    @classmethod
    def setUpClass(cls):
        proc, http_port, ssl_port = cls.init_test_server()
        cls.proc = proc
        try:
            cls.api_url = "http://localhost:%d/api" % http_port
            cls.api_url_ssl = "https://localhost:%d/api" % ssl_port
        except:
            cls.kill_test_server()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.kill_test_server()

    def setUp(self):
        self.client = HessianProxy(self.api_url, version=self.version)

    def tearDown(self):
        if self.client and getattr(self.client, '_client', None):
            self.client._client.close()

    @classmethod
    def init_test_server(cls, timeout=10):
        proc = Popen(["java", "-jar", TEST_JAR], stdout=PIPE, stderr=PIPE)

        # Start thread timer so we can kill the process if it times out
        timer = Timer(timeout,
            lambda p: p.kill() or setattr(p, 'timed_out', True), [proc])
        timer.start()

        http_port = None
        ssl_port = None
        stderr = b''

        while True:
            rlist = select.select(
                [proc.stdout.fileno(), proc.stderr.fileno()], [], [])[0]

            line = None

            for fileno in rlist:
                if fileno == proc.stdout.fileno():
                    line = proc.stdout.readline()
                elif fileno == proc.stderr.fileno():
                    stderr += proc.stderr.readline()

            if line is not None:
                matches = re_port_number.search(line.decode('utf-8'))
                if matches:
                    http_port = matches.group('http_port')
                    ssl_port = matches.group('ssl_port')
                    timer.cancel()
                    break

            if proc.poll() is not None:
                if getattr(proc, 'timed_out', False):
                    raise Exception("Timed out waiting for port\n%s" % stderr.decode('utf-8'))
                else:
                    raise Exception("Process terminated unexpectedly\n%s" % stderr.decode('utf-8'))

        return proc, int(http_port), int(ssl_port)

    @classmethod
    def kill_test_server(cls):
        if cls.proc:
            try:
                cls.proc.stdout.close()
            except:
                pass
            try:
                cls.proc.stderr.close()
            except:
                pass
            os.kill(cls.proc.pid, signal.SIGKILL)
            cls.proc.wait()
            cls.proc = None
