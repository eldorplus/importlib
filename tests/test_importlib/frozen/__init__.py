from .. import test_suite
import os.path
from test import support
import unittest


def test_suite():
    directory = os.path.dirname(__file__)
    return test_suite('importlib.test.frozen', directory)


load_tests = support.make_load_tests(__file__)


if __name__ == '__main__':
    from test.support import run_unittest
    run_unittest(test_suite())
