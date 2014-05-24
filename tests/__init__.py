from contextlib import contextmanager
import os.path
import sys
import unittest


TEST_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(TEST_ROOT)


# Swap in importlib2.
sys.path.insert(0, PROJECT_ROOT)  # Force the right importlib2.
import importlib2

# Fix up the stdlib.
from importlib2._fixers import _stdlib as _fixers
_fixers.fix_collections()
_fixers.fix_unittest()
_fixers.inject_threading()

# Inject importlib.
import importlib2.hook
importlib2.hook.inject()

# Swap in tests.
from . import support
_fixers.fix_support(support)
sys.modules['test'] = sys.modules[__name__]
sys.modules['test.support'] = support
from . import lock_tests
sys.modules['test.lock_tests'] = lock_tests

# Install the hook.
importlib2.hook.install(_inject=False)
