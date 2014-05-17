try:
    builtins = __import__('builtins')
except ImportError:
    builtins = __import__('__builtin__')
import sys


NAME = 'cpython'


class NewImportError(builtins.ImportError):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', None)
        self.path = kwargs.pop('path', None)
        super(ImportError, self).__init__(*args, **kwargs)


def fix_imp(_imp=None):
    if _imp is None:
        try:
            import _imp as _imp
        except ImportError:
            import imp as _imp
    sys.modules.setdefault('_imp', _imp)
    if not hasattr(_imp, 'extension_suffixes'):
        ext_suffixes = []
        _imp.extension_suffixes = lambda: ext_suffixes
    if not hasattr(_imp, '_fix_co_filename'):
        _imp._fix_co_filename = lambda co, sp: None
    if not hasattr(_imp, 'is_frozen_package'):
        def is_frozen_package(name):
            # XXX Finish this.
            return False
        _imp.is_frozen_package = is_frozen_package


def fix_sys(sys):
    if not hasattr(sys, 'implementation'):
        types = fix_types()
        impl = types.SimpleNamespace()
        impl.name = NAME
        impl.version = sys.version_info
        impl.hexversion = sys.hexversion
        major, minor = sys.version_info[:2]
        impl.cache_tag = '{}-{}{}'.format(NAME, major, minor)
        sys.implementation = impl


def inject_importlib(name):
    if not name.startswith('importlib2'):
        return
    mod = sys.modules[name]
    newname = name.replace('importlib2', 'importlib')
    sys.modules[newname] = mod


def fix_bootstrap(bootstrap, sys, imp):
    inject_importlib(bootstrap.__name__)

    # XXX Inject _boostrap into _frozen_importlib (if it exists)?
    if not sys.modules.get('importlib._bootstrap'):
        sys.modules['_frozen_importlib'] = bootstrap

    fix_builtins()
    fix_sys(sys)
    fix_imp(imp)
    fix_os()
    fix_io()
    fix_thread()

    class Module(type(sys)):
        def __init__(self, name):
            super(Module, self).__init__(name)
            self.__spec__ = None
            self.__loader__ = None
        def __repr__(self):
            return bootstrap._module_repr(self)
    Module.__module__ = bootstrap.__name__
    bootstrap._new_module = Module


def fix_os(os=None):
    if os is None:
        os = __import__('os')
    _os = __import__(os.name)
    if not hasattr(_os, 'replace'):
        # better than nothing
        def replace(src, dst):
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(src, dst)
        _os.replace = replace
    if not hasattr(os, 'fsencode'):
        os.fsencode = lambda s: s
    if not hasattr(os, 'fsdecode'):
        os.fsdecode = lambda s: s


def fix_io():
    import _io


def fix_builtins(builtins=builtins):
    sys.modules.setdefault('builtins', builtins)


def fix_collections():
    try:
        import collections.abc
    except ImportError:
        import collections
        collections.abc = collections
        sys.modules['collections.abc'] = collections


def fix_threading():
    from . import threading
    sys.modules['threading'] = threading


def fix_thread():
    try:
        import _thread
    except ImportError:
        import thread as _thread
        sys.modules['_thread'] = _thread
    if not hasattr(_thread, 'TIMEOUT_MAX'):
        _thread.TIMEOUT_MAX = 10  # XXX Make it accurate.

    if not hasattr(_thread, '_set_sentinel'):
        _thread._set_sentinel = lambda: _thread.allocate_lock()


def fix_types():
    import types
    if not hasattr(types, 'SimpleNamespace'):
        class SimpleNamespace(object):
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
            def __repr__(self):
                keys = sorted(self.__dict__)
                items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
                return "{}({})".format(type(self).__name__, ", ".join(items))
            def __eq__(self, other):
                return self.__dict__ == other.__dict__
            def __ne__(self, other):
                return not(self == other)
        types.SimpleNamespace = SimpleNamespace
    if not hasattr(types, 'new_class'):
        def new_class(name, bases=(), kwds=None, exec_body=None):
            if kwds and 'metaclass' in kwds:
                meta = kwds['metaclass']
            else:
                meta = type
            ns = {}
            if exec_body is not None:
                exec_body(ns)
            return meta(name, bases, ns)
        types.new_class = new_class
    return types


def fix_unittest():
    import unittest
    from contextlib import contextmanager
    @contextmanager
    def subTest(self, *args, **kwargs):
        yield
    unittest.TestCase.subTest = subTest


def kwonly(names):
    if isinstance(names, str):
        names = names.replace(',', ' ').split()
    def decorator(f):
        # XXX Return a wrapper that enforces kw-only.
        return f
    return decorator


PY3 = (sys.hexversion > 0x03000000)

# Based on six.exec_().
if PY3:
    exec_ = getattr(builtins, 'exec')
else:
    def exec_(_code_, _globs_, _locs_=None):
        """Execute code in a namespace."""
        if _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")
