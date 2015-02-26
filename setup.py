import os, sys
from setuptools import find_packages, setup
from pyhessian import __version__

if sys.version_info < (2, 7):
    raise NotImplementedError("python-hessian requires Python 2.7 or later")

setup(
    name = "python-hessian",
    version = __version__,
    description = "Hessian RPC Library",
    long_description = open(
        os.path.join(
            os.path.dirname(__file__),
            'README.rst'
        )
    ).read(),

    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Object Brokering',
        'Topic :: Software Development :: Libraries',
    ],

    url = "https://github.com/theatlantic/python-hessian",

    author = "Frankie Dintino",
    author_email = "fdintino@theatlantic.com",
    license = "BSD",

    platforms = "any",
    packages = find_packages(exclude=["test"]),
    zip_safe = True,
)

