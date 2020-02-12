import os
import sys

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test as TestCommand
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test as TestCommand


if sys.version_info < (2, 6):
    raise NotImplementedError("python-hessian requires Python 2.6 or later")


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
    version='1.1.2',
    description="Hessian RPC Library",
    long_description=open(
        os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Object Brokering',
        'Topic :: Software Development :: Libraries',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    url="https://github.com/theatlantic/python-hessian",
    install_requires=['six>=1.7.0'],
    author="Frankie Dintino",
    author_email="fdintino@theatlantic.com",
    license="BSD",
    tests_require=['tox'],
    cmdclass={'test': Tox},
    platforms="any",
    packages=find_packages(exclude=["test"]),
    zip_safe=True)
