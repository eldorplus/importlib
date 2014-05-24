try:
    builtins = __import__('builtins')
except ImportError:
    builtins = __import__('__builtin__')
from contextlib import contextmanager
import imp
import sys
import types


@contextmanager
def swap(obj, attr, value, pop=True):
    original = getattr(obj, attr)
    setattr(obj, attr, value)
    try:
        yield original if pop else value
    finally:
        setattr(obj, attr, original)


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
            from ._core import fix_sys
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
        # XXX Change to reflect injection?
        cache_tag = '{}-{}{}'.format(name, major, minor)

    if not hasattr(types, 'SimpleNamespace'):
        from ._core import fix_types
        fix_types()
    impl = types.SimpleNamespace()
    impl.name = name
    impl.version = version
    impl.hexversion = hexversion
    impl.cache_tag = cache_tag
    return impl


#################################################
# custom implementations

try:
    SimpleNamespace = types.SimpleNamespace
except AttributeError:
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

try:
    new_class = types.new_class
except AttributeError:
    def new_class(name, bases=(), kwds=None, exec_body=None):
        if kwds and 'metaclass' in kwds:
            meta = kwds['metaclass']
        else:
            meta = type
        ns = {}
        if exec_body is not None:
            exec_body(ns)
        return meta(name, bases, ns)


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
def inject_importlib(name, _target='importlib2'):
    # for importlib2 and its submodules
    mod = sys.modules[name]

    if name != _target:
        if not name.startswith(_target+'.'):
            return
        importlib = sys.modules.get('importlib')
        if importlib and importlib.__name__ != _target:
            # Only clobber if importlib got clobbered.
            return
    else:
        importlib = mod

    # XXX Copy into existing namespace instead of replacing?
    newname = name.replace('importlib2', 'importlib')
    sys.modules[newname] = mod

    # Keep a reference to _bootstrap so it doesn't get garbage collected.
    if not hasattr(mod, '_bootstrap'):
        mod._boostrap = sys.modules['importlib2']._bootstrap


#################################################
# for importlib2.__init__()

def fix_importlib(name):
    from ._core import fix_sys, fix_imp, fix_types, fix_warnings
    mod = sys.modules[name]
    fix_types()  # Needed for fix_sys().
    fix_warnings()
    fix_sys(mod.sys)
    fix_imp(mod._imp)


def fix_bootstrap(bootstrap):
    from ._core import fix_builtins, fix_os, fix_io, fix_thread
    fix_builtins()
    fix_os()
    fix_io()
    fix_thread()

    bootstrap.MAGIC_NUMBER = get_magic()

    from ._modules import fix_moduletype
    fix_moduletype(bootstrap)
