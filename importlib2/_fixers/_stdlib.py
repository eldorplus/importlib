import imp
import sys

from . import swap


# Additive but idempotent.
def fix_collections():
    try:
        import collections.abc
    except ImportError:
        import collections
        collections.abc = collections
        sys.modules['collections.abc'] = collections


# Additive but idempotent.
def fix_unittest():
    import unittest
    if not hasattr(unittest.TestCase, 'subTest'):
        from contextlib import contextmanager
        @contextmanager
        def subTest(self, *args, **kwargs):
            yield
        unittest.TestCase.subTest = subTest
    try:
        import unittest.mock
    except ImportError:
        def patched(obj, attr):
            def mocked(*args, **kwargs):
                try:
                    exc = mocked.side_effect
                except AttributeError:
                    return mocked.return_value
                else:
                    raise exc
            return swap(obj, attr, mocked, pop=False)
        mock = type(unittest)('mock')
        mock.patch = lambda: None
        mock.patch.object = patched
        sys.modules['unittest.mock'] = mock
        unittest.mock = mock


# Destructive!
def inject_threading():
    from . import threading
    sys.modules['threading'] = threading
