"""Utils to swap types in the import state."""

from contextlib import contextmanager
import imp
import sys

from . import machinery


@contextmanager
def locked():
    imp.acquire_lock()
    try:
        yield
    finally:
        imp.release_lock()


def overwrite_container(obj, values):
    setter = obj.__setitem__
    if hasattr(values, 'items'):
        # mapping
        items = values.items()
    elif hasattr(values, '__getitem__'):
        # sequence
        items = enumerate(values)
    else:
        try:
            # iterable of pairs
            items = [(k, v) for k, v in values]
        except TypeError:
            # iterable of values
            items = enumerate(values)
    for key, value in items:
        setter(key, value)


def swap_finder(finder):
    if isinstance(finder, type):
        cls = None
        typename = finder.__name__
    else:
        cls = finder.__class__
        typename = cls.__name__
    if '.' not in typename:
        return finder
    modname, _, name = typename.rpartition('.')
    if modname != '_frozen_importlib':
        return finder
    # Switch over to the type from importlib2.
    cls2 = getattr(machinery, name)
    if cls is None:
        return cls2
    raise NotImplementedError


def swap_path_hook(hook):
    print(hook)
    return hook


def swap_import_state(name, values=None):
    state = getattr(sys, name)
    copied = state.__class__(state)
    if values is None:
        if name == 'meta_path':
            values = (swap_finder(finder) for finder in state)
        elif name == 'path_hooks':
            values = (swap_path_hook(hook) for hook in state)
        elif name == 'path_importer_cache':
            values = ((path, swap_finder(finder))
                      for path, finder in state.items())
        else:
            raise NotImplementedError
    overwrite_container(state, values)
    return copied


def swap_all():
    with locked():
        meta_path = swap_import_state('meta_path')
        hooks = swap_import_state('path_hooks')
        cache = swap_import_state('path_importer_cache')

    @contextmanager
    def cm():
        try:
            yield
        finally:
            swap_import_state('meta_path', meta_path)
            swap_import_state('path_hooks', hooks)
            swap_import_state('path_importer_cache', cache)
    return cm()
