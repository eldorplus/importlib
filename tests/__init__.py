import imp
import os.path
import sys


TEST_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(TEST_ROOT)


def make_load_tests(modfilename):
    topdir = PROJECT_ROOT
    startdir = os.path.dirname(modfilename)
    def load_tests(loader, tests, pattern):
        pkgtests = loader.discover(startdir, pattern or 'test*.py', topdir)
        tests.addTests(pkgtests)
        return tests
    return load_tests


#################################################
# Fix up tests and inject importlib2.

imp._testing_importlib2 = True

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
importlib2.hook.install(_inject=False)

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
