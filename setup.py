import os
import sys
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

from pyhessian import __version__

if sys.version_info < (2, 7):
    raise NotImplementedError("python-hessian requires Python 2.7 or later")


class Tox(TestCommand):

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        errno = tox.cmdline()
        sys.exit(errno)


setup(
    name="python-hessian",
    version=__version__,
    description="Hessian RPC Library",
    long_description=open(
        os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Object Brokering',
        'Topic :: Software Development :: Libraries',
    ],

    url="https://github.com/theatlantic/python-hessian",

    author="Frankie Dintino",
    author_email="fdintino@theatlantic.com",
    license="BSD",
    tests_require=['tox'],
    cmdclass={'test': Tox},
    platforms="any",
    packages=find_packages(exclude=["test"]),
    zip_safe=True)
