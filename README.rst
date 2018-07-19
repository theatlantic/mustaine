python-hessian
==============

.. image:: https://travis-ci.org/theatlantic/python-hessian.svg?branch=master
    :target: https://travis-ci.org/theatlantic/python-hessian

**python-hessian** is a Python implemention of Hessian, a binary web services
protocol. It supports the `Hessian 1.0.2 specification
<http://hessian.caucho.com/doc/hessian-1.0-spec.xtp>`_ and the
`Hessian 2.0 Serialization Protocol
<http://hessian.caucho.com/doc/hessian-serialization.html>`_. The library
is a fork of `mustaine <https://github.com/bgilmore/mustaine>`_, which is no
longer maintained. It provides a standard HTTP-based client
as well as a general-purpose serialization library.

Usage
-----

Using ``pyhessian.client``
..........................

Testing against `Caucho’s <http://hessian.caucho.com/>`_ reference service:

.. code-block:: python

   from pyhessian.client import HessianProxy
   service = HessianProxy("http://hessian.caucho.com/test/test")
   print service.replyDate_1()

Source
------

Up-to-date sources and documentation can always be found at the `python-hessian
GitHub site <https://github.com/theatlantic/python-hessian>`_.
