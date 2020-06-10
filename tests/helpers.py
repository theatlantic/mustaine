import os
import re
from subprocess import Popen, PIPE
import select
import signal
from threading import Timer


SUPPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'support'))
TEST_JAR = os.path.join(SUPPORT_DIR, 'hessian-test-servlet.jar')

re_port_numbers = re.compile(
    r'Listening on http port: (?P<http_port>\d+), '
    r'ssl port: (?P<ssl_port>\d+)$')


class ServletProcessWrapper(object):
    http_port = None
    ssl_port = None

    def __init__(self, timeout=10):
        self.proc = Popen(["java", "-jar", TEST_JAR], stdout=PIPE, stderr=PIPE)

        # Start thread timer so we can kill the process if it times out
        timer = Timer(timeout,
            lambda p: p.kill() or setattr(p, 'timed_out', True), [self.proc])
        timer.start()

        stderr = b''

        while True:
            rlist = select.select(
                [self.proc.stdout.fileno(), self.proc.stderr.fileno()], [], [])[0]

            line = None

            for fileno in rlist:
                if fileno == self.proc.stdout.fileno():
                    line = self.proc.stdout.readline()
                elif fileno == self.proc.stderr.fileno():
                    stderr += self.proc.stderr.readline()

            if line is not None:
                matches = re_port_numbers.search(line.decode('utf-8'))
                if matches:
                    self.http_port = int(matches.group('http_port'))
                    self.ssl_port = int(matches.group('ssl_port'))
                    timer.cancel()
                    break

            if self.proc.poll() is not None:
                if getattr(self.proc, 'timed_out', False):
                    raise Exception("Timed out waiting for port\n%s" % stderr.decode('utf-8'))
                else:
                    raise Exception("Process terminated unexpectedly\n%s" % stderr.decode('utf-8'))

    @property
    def http_url(self):
        if self.http_port:
            return "http://localhost:%d/api" % self.http_port

    @property
    def http_auth_url(self):
        if self.http_port:
            return "http://admin:password@localhost:%d/api" % self.http_port

    @property
    def https_url(self):
        if self.ssl_port:
            return "https://localhost:%d/api" % self.ssl_port

    def __del__(self):
        if self.proc:
            try:
                self.proc.stdout.close()
            except:
                pass
            try:
                self.proc.stderr.close()
            except:
                pass
            os.kill(self.proc.pid, signal.SIGKILL)
            self.proc.wait()
            self.proc = None
