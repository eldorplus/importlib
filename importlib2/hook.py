from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import __builtin__ as builtins
except ImportError:
    import builtins
from contextlib import contextmanager

from . import __import__ as _import, _bootstrap, sys as _sys, _imp


@contextmanager
def _locked():
    _imp.acquire_lock()
    try:
        yield
    finally:
        _imp.release_lock()


def _clear(container):
    copied = container.__class__(container)
    try:
        clear = container.clear
    except AttributeError:
        for _ in copied:
            container.pop()
    else:
        clear()
    return copied


def _inject(container, values, clear=False):
    if clear:
        copied = _clear(container)
    else:
        copied = None
    for i, value in enumerate(values):
        container.insert(i, value)
    return copied


def _get_finders():
    finders = []
    for finder in _sys.meta_path:
        modname = getattr(finder, '__module__', finder.__class__.__module__)
        if modname == '_frozen_importlib':
            continue
        finders.append(finder)
    return finders


def _get_hooks():
    hooks = []
    for hook in _sys.path_hooks:
        if hook.__module__ == '_frozen_importlib':
            continue
        hooks.append(hook)
    return hooks


def install():
    with _locked():
        finders = _get_finders()
        hooks = _get_hooks()

        meta_path = _clear(_sys.meta_path)
        path_hooks = _clear(_sys.path_hooks)
        cache = _clear(_sys.path_importer_cache)
        original = builtins.__import__

        _bootstrap._install(_sys, _imp)
        _inject(_sys.meta_path, finders)
        _inject(_sys.path_hooks, hooks)
        builtins.__import__ = _import

    @contextmanager
    def cm():
        try:
            yield
        finally:
            with _locked():
                _inject(_sys.meta_path, meta_path, clear=True)
                _inject(_sys.path_hooks, path_hooks, clear=True)
                _inject(_sys.path_importer_cache, cache, clear=True)
                builtins.__import__ = original
    return cm()
