try:
    import unittest2 as unittest
except ImportError:
    import unittest

from .test_encoding import EncoderTestCase
from .test_parser import ParserV1TestCase, ParserV2TestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EncoderTestCase))
    suite.addTest(unittest.makeSuite(ParserV1TestCase))
    suite.addTest(unittest.makeSuite(ParserV2TestCase))
    return suite
