try:
    import __builtin__ as builtins
except ImportError:
    import builtins
from contextlib import contextmanager

from . import _swap, __import__ as _import


def install():
    with _swap.locked():
        original = builtins.__import__
        builtins.__import__ = _import
        meta_path = _swap.swap_import_state('meta_path')
        hooks = _swap.swap_import_state('path_hooks')
        cache = _swap.swap_import_state('path_importer_cache')

    @contextmanager
    def cm():
        try:
            yield
        finally:
            with _swap.locked():
                _swap.swap_import_state('meta_path', meta_path)
                _swap.swap_import_state('path_hooks', hooks)
                _swap.swap_import_state('path_importer_cache', cache)
                builtins.__import__ = original
    return cm()
