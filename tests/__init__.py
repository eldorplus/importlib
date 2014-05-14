from contextlib import contextmanager
import os.path
import sys
import unittest


TEST_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(TEST_ROOT)


def inject_importlib2():
    sys.path.insert(0, PROJECT_ROOT)  # Force the right importlib2.
    import importlib2
    sys.modules['importlib'] = importlib2
    from importlib2 import abc, machinery, util
    sys.modules['importlib.abc'] = abc
    sys.modules['importlib.machinery'] = machinery
    sys.modules['importlib.util'] = util
    return importlib2


# Swap in importlib2.
importlib2 = inject_importlib2()

# Fix up the stdlib.
from importlib2 import _fixers
_fixers.fix_collections()
_fixers.fix_types()
_fixers.fix_unittest()

# Swap in tests.
from . import support
sys.modules['test'] = sys.modules[__name__]
sys.modules['test.support'] = support
from . import lock_tests
sys.modules['test.lock_tests'] = lock_tests

# Install the hook.
import importlib2.hook
importlib2.hook.install()
