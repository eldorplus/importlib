import imp
import sys
import types

from . import builtins, SimpleNamespace, new_class, get_magic, get_ext_suffixes


# Additive but idempotent.
def fix_types(types=types):
    types.SimpleNamespace = SimpleNamespace
    types.new_class = new_class
    return types


# Additive but idempotent.
def fix_sys(sys=sys):
    if not hasattr(sys, 'implementation'):
        sys.implementation = make_impl()
    get_magic()  # Force setting of sys.implementation.pyc_magic_bytes.


# Additive but idempotent.
def fix_imp(_imp=None, imp=imp):
    if _imp is None:
        try:
            import _imp
        except ImportError:
            _imp = imp
    elif _imp.__name__ == 'imp':
        imp = _imp
    elif _imp.__name__ != '_imp':
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


# ???
def fix_warnings():
    import warnings
