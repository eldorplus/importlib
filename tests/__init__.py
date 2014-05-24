import os.path
import sys


TEST_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(TEST_ROOT)

# Swap in importlib2.
sys.path.insert(0, PROJECT_ROOT)  # Force the right importlib2.
import importlib2

# Fix up the stdlib.
from ._fixers import _stdlib as _fixers
_fixers.fix_builtins()
_fixers.fix_collections()
_fixers.fix_tempfile()
_fixers.fix_unittest()
_fixers.fix_os()
_fixers.fix_types()
_fixers.fix_thread()
_fixers.inject_threading()

# Inject importlib and __import__.
import importlib2.hook
importlib2.hook.inject()
importlib2.hook.install()

# Swap in tests.
from . import support
_fixers.fix_support(support)
sys.modules['test'] = sys.modules[__name__]
sys.modules['test.support'] = support
from . import lock_tests
sys.modules['test.lock_tests'] = lock_tests
