try:
    builtins = __import__('builtins')
except ImportError:
    builtins = __import__('__builtin__')
import imp
import sys


#################################################
# data external to importlib

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


# Additive but idempotent.
def get_magic():
    try:
        return sys.implementation.pyc_magic_bytes
    except AttributeError:
        if not hasattr(sys, 'implementation'):
            # XXX Should not be necessary!
            fix_sys(sys)
        sys.implementation.pyc_magic_bytes = imp.get_magic()
        return sys.implementation.pyc_magic_bytes


# inert/informational
def get_ext_suffixes(imp):
    return [s for s, _, t in imp.get_suffixes() if t == imp.C_EXTENSION]


# Additive but idempotent.
def make_impl(name=None, version=None, cache_tag=None):
    hexversion = None
    if name is None:
        import platform
        name = platform.python_implementation().lower()
    if version is None:
        version = sys.version_info
        hexversion = getattr(sys, 'hexversion', None)
    major, minor, micro, releaselevel, serial = version
    if hexversion is None:
        assert releaselevel in ('alpha', 'beta', 'candidate', 'final')
        assert serial < 10
        hexversion = '0x{:x}{:>02x}{:>02x}{}{}'.format(major, minor, micro,
                                                       releaselevel[0], serial)
        hexversion = int(hexversion, 16)
    if cache_tag is None:
        cache_tag = '{}-{}{}'.format(name, major, minor)

    types = fix_types()
    impl = types.SimpleNamespace()
    impl.name = name
    impl.version = version
    impl.hexversion = hexversion
    impl.cache_tag = cache_tag
    return impl


#################################################
# only for importlib

def kwonly(names):
    # decorator factory to replace the kw-only syntax
    if isinstance(names, str):
        names = names.replace(',', ' ').split()
    def decorator(f):
        # XXX Return a wrapper that enforces kw-only.
        return f
    return decorator


# Destructive but idempotent.
def inject_importlib(name, *, _target='importlib2'):
    # for importlib2 and its submodules
    if name != _target:
        if not name.startswith(_target+'.'):
            return
        importlib = sys.modules.get('importlib')
        if importlib and importlib.__name__ != _target:
            # Only clobber if importlib got clobbered.
            return

    mod = sys.modules[name]
    # XXX Copy into existing namespace instead of replacing?
    newname = name.replace('importlib2', 'importlib')
    sys.modules[newname] = mod


#################################################
# for importlib2.__init__()

# None of these should be destructive!

# Additive but idempotent.
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


# Additive but idempotent.
def fix_sys(sys):
    if not hasattr(sys, 'implementation'):
        sys.implementation = make_impl()
    get_magic()  # Force setting of sys.implementation.pyc_magic_bytes.


# Additive but idempotent.
def fix_imp(_imp=None):
    if _imp is None:
        try:
            import _imp
        except ImportError:
            import imp
            _imp = imp
    elif _imp.__name__ == 'imp':
        imp = _imp
    elif _imp.__name__ == '_imp':
        import imp
    else:
        raise RuntimeError('unrecognized imp: {!r}'.format(_imp.__name__))
    # fix _imp
    if '_imp' not in sys.modules:
        sys.modules['_imp'] = _imp
    if not hasattr(imp, 'extension_suffixes'):
        ext_suffixes = get_ext_suffixes(imp)
        _imp.extension_suffixes = lambda: ext_suffixes
    if not hasattr(_imp, '_fix_co_filename'):
        # XXX Finish this?
        _imp._fix_co_filename = lambda co, sp: None
    if not hasattr(_imp, 'is_frozen_package'):
        def is_frozen_package(name):
            # XXX Finish this?  Were frozen packages always allowed?
            return False
        _imp.is_frozen_package = is_frozen_package
    # fix imp
    imp  # XXX Is there anything to fix?


def fix_bootstrap(bootstrap):
    fix_builtins()
    fix_os()
    fix_io()
    fix_thread()

    bootstrap.MAGIC_NUMBER = get_magic()

    # Set a custom module type.
    class Module(type(sys)):
        def __init__(self, name):
            super(Module, self).__init__(name)
            self.__spec__ = None
            self.__loader__ = None
        def __repr__(self):
            return bootstrap._module_repr(self)
    Module.__module__ = bootstrap.__name__
    bootstrap._new_module = Module


# Additive but idempotent.
def fix_builtins(builtins=builtins):
    sys.modules.setdefault('builtins', builtins)


# Additive but idempotent.
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


# ???
def fix_io():
    import _io


# Additive but idempotent.
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


#################################################
# for tests

# These may be destructive.

# Additive but idempotent.
def fix_collections():
    try:
        import collections.abc
    except ImportError:
        import collections
        collections.abc = collections
        sys.modules['collections.abc'] = collections


# Destructive!
def fix_threading():
    from . import threading
    sys.modules['threading'] = threading


# Additive but idempotent.
def fix_unittest():
    import unittest
    if not hasattr(unittest.TestCase, 'subTest'):
        from contextlib import contextmanager
        @contextmanager
        def subTest(self, *args, **kwargs):
            yield
        unittest.TestCase.subTest = subTest
