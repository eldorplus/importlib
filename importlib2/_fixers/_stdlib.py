import sys

from . import swap
from ._modules import mod_from_ns


# Additive but idempotent.
def fix_collections():
    try:
        import collections.abc
    except ImportError:
        import collections
        collections.abc = collections
        sys.modules['collections.abc'] = collections


# Destructive!
def inject_threading():
    from . import threading
    sys.modules['threading'] = threading


#################################################
# testing

# Additive but idempotent.
def fix_unittest():
    import unittest

    # Add in unittest.TestCase.subTest.
    if not hasattr(unittest.TestCase, 'subTest'):
        from contextlib import contextmanager
        @contextmanager
        def subTest(self, *args, **kwargs):
            yield
        unittest.TestCase.subTest = subTest

    # Add in a fake unittest.mock.
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
        from importlib2 import _bootstrap
        mock = _bootstrap._new_module('unittest.mock')
        mock.__loader__ = _bootstrap.BuiltinImporter
        mock.__spec__ = _bootstrap.ModuleSpec(mock.__name__, mock.__loader__,
                                              origin=__file__)
        mock.patch = lambda: None
        mock.patch.object = patched
        sys.modules['unittest.mock'] = mock
        unittest.mock = mock


def _format_obj(obj):
    if isinstance(obj, dict) and '__builtins__' in obj:
        refmod = mod_from_ns(obj)
        return ('<ns for module {!r} ({} {})>'
                ).format(obj['__name__'], refmod, id(refmod))
    else:
        return '{} {}'.format(obj, id(obj))


def check_mod(module_name, mod=None, orig=None):
    if module_name is None:
        if mod is None:
            raise TypeError('missing module_name')
        module_name = mod.__name__
        if module_name is None:
            raise ImportError('{!r}: mod.__name__ is None'.format(mod))
    if mod is None:
        if module_name not in sys.modules:
            return
        mod = sys.modules[module_name]

    # Check the module.
    if module_name.startswith('importlib'):
        if not hasattr(mod, '_bootstrap'):
            try:
                f = mod._resolve_name
            except AttributeError:
                f = mod.ModuleSpec.__init__
            bsname = f.__globals__['__name__']
            assert bsname is not None, module_name


# Additive but idempotent.
def fix_support(support=None):
    if support is None:
        from tests import support

    if not hasattr(support, 'check_mod'):
        support.check_mod = check_mod
