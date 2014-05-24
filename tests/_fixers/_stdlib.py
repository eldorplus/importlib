import os
import shutil
import sys
import tempfile
import types

from importlib2._fixers import (swap, SimpleNamespace, new_class,
                                _thread, builtins)
from importlib2._fixers._modules import mod_from_ns


def fix_builtins(builtins=builtins):
    sys.modules.setdefault('builtins', builtins)


def fix_types(types=types):
    types.SimpleNamespace = SimpleNamespace
    types.new_class = new_class
    return types


def fix_collections():
    try:
        import collections.abc
    except ImportError:
        import collections
        collections.abc = collections
        sys.modules['collections.abc'] = collections


def fix_tempfile():
    if not hasattr(tempfile, 'TemporaryDirectory'):
        class TemporaryDirectory(object):
            def __init__(self):
                self.name = tempfile.mkdtemp()
            def __enter__(self):
                return self
            def __exit__(self, *args):
                shutil.rmtree(self.name, ignore_errors=True)
        tempfile.TemporaryDirectory = TemporaryDirectory


def fix_os(os=os):
    if not hasattr(os, 'fsencode'):
        os.fsencode = lambda s: s
    if not hasattr(os, 'fsdecode'):
        os.fsdecode = lambda s: s


def fix_thread(_thread=_thread):
    sys.modules['_thread'] = _thread

    if not hasattr(_thread, 'TIMEOUT_MAX'):
        _thread.TIMEOUT_MAX = 10  # XXX Make it accurate.

    if not hasattr(_thread, '_set_sentinel'):
        _thread._set_sentinel = lambda: _thread.allocate_lock()


def inject_threading():
    from . import threading
    sys.modules['threading'] = threading


#################################################
# testing

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


def fix_support(support=None):
    if support is None:
        from tests import support

    if not hasattr(support, 'check_mod'):
        support.check_mod = check_mod
