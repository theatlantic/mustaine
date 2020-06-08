#!/usr/bin/env python

import sys
import unittest
import warnings

warnings.simplefilter("error", Warning)

from tests import all_tests  # noqa


if __name__ == "__main__":
    tests = all_tests()
    results = unittest.TextTestRunner().run(tests)
    if results.failures or results.errors:
        sys.exit(1)
