import os.path
import sys


TEST_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(TEST_ROOT)

# Swap in importlib2.
sys.path.insert(0, PROJECT_ROOT)  # Force the right importlib2.
import importlib2

# Fix up the stdlib.
from ._fixers import _stdlib
_stdlib.fix_builtins()
_stdlib.fix_collections()
_stdlib.fix_tempfile()
_stdlib.fix_unittest()
_stdlib.fix_os()
_stdlib.fix_types()
_stdlib.fix_thread()
_stdlib.inject_threading()

# Inject importlib and __import__.
import importlib2.hook
importlib2.hook.inject()
importlib2.hook.install()

# Swap in tests.
from . import support
_stdlib.fix_support(support)
sys.modules['test'] = sys.modules[__name__]
sys.modules['test.support'] = support
from . import lock_tests
sys.modules['test.lock_tests'] = lock_tests

# Fix specific tests.
from ._fixers import _tests
_tests.fix_test_source_encodings()
