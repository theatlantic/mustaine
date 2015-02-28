import os
import re
from subprocess import Popen, PIPE
import select
from threading import Timer

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pyhessian.client import HessianProxy


SUPPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'support'))
TEST_JAR = os.path.join(SUPPORT_DIR, 'hessian-test-servlet.jar')

re_port_number = re.compile(r'Listening on port: (\d+)$')


class HessianTestCase(unittest.TestCase):

    version = 1
    proc = None
    api_url = None

    @classmethod
    def setUpClass(cls):
        try:
            proc, port_num = cls.init_test_server()
        except:
            # Fall back to public test server
            cls.api_url = "http://hessian.caucho.com/test/test"
        else:
            cls.proc = proc
            cls.api_url = "http://localhost:%d/api" % port_num

    @classmethod
    def tearDownClass(cls):
        if cls.proc:
            cls.proc.kill()

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

        port_num = None
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
                port_num_matches = re_port_number.search(line.decode('utf-8'))
                if port_num_matches:
                    port_num = int(port_num_matches.group(1))
                    timer.cancel()
                    break

            if proc.poll() != None:
                if getattr(proc, 'timed_out', False):
                    raise Exception("Timed out waiting for port\n%s" % stderr.decode('utf-8'))
                else:
                    raise Exception("Process terminated unexpectedly\n%s" % stderr.decode('utf-8'))

        return proc, port_num
