from .. import test_suite
import os
from test import support


def test_suite():
    directory = os.path.dirname(__file__)
    return test_suite('importlib.test.builtin', directory)


load_tests = support.make_load_tests(__file__)


if __name__ == '__main__':
    from test.support import run_unittest
    run_unittest(test_suite())
