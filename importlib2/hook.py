from __future__ import absolute_import, division, print_function, unicode_literals

from contextlib import contextmanager
import os
import sys

from . import _bootstrap, _fixers


@contextmanager
def _locked():
    _bootstrap._imp.acquire_lock()
    try:
        yield
    finally:
        _bootstrap._imp.release_lock()


#################################################
# import state helpers

def _get_old_default_finders(finders):
    # The only metapath finder classes in _boostrap are defaults.
    oldfinders = []
    for finder in finders:
        modname = getattr(finder, '__module__',
                          finder.__class__.__module__)
        if modname == '_frozen_importlib':
            oldfinders.append(finder)
    return oldfinders


def _remove_old_default_finders(finders):
    # Remove 3.4+ defaults from sys.meta_path.
    oldfinders = _get_old_default_finders(finders)
    for finder in oldfinders:
        finders.remove(finder)
    return oldfinders


def _add_default_finders(finders):
    # See _bootstrap._install().
    finders.append(_bootstrap.BuiltinImporter)
    finders.append(_bootstrap.FrozenImporter)
    if os.name == 'nt':
        finders.append(_bootstrap.WindowsRegistryFinder)
    finders.append(_bootstrap.PathFinder)


def _replace_finders(finders):
    old = _remove_old_default_finders(finders)
    _add_default_finders(finders)
    return old


def _get_old_default_hooks(hooks):
    # The only hooks from _bootstrap come from FileFinder.
    oldhooks = []
    for hook in hooks:
        if hook.__module__ == '_frozen_importlib':
            oldhooks.append(hook)
    # XXX Include imp.NullImporter?
    return oldhooks


def _remove_old_default_hooks(hooks):
    # Remove 3.4+ defaults from sys.path_hooks.
    oldhooks = _get_old_default_hooks(hooks)
    for hook in oldhooks:
        hooks.remove(hook)
    return oldhooks


def _add_default_hooks(hooks):
    # See _bootstrap._install().
    supported_loaders = _bootstrap._get_supported_file_loaders()
    hook = _bootstrap.FileFinder.path_hook(*supported_loaders)
    hooks.extend([hook])


def _replace_hooks(hooks):
    old = _remove_old_default_hooks(hooks)
    _add_default_hooks(hooks)
    return old


def _fix_import_state():
    _replace_hooks(sys.path_hooks)
    _replace_finders(sys.meta_path)
    sys.path_importer_cache.clear()


#################################################
# modules

def _get_parent(mod):
    parent = mod.__name__.rpartition('.')[0]
    return sys.modules[parent] if parent else None


def _get_path(mod):
    parent = _get_parent(mod)
    if not parent:
        return sys.path
    else:
        return parent.__path__


def _get_spec(mod):
    spec = getattr(mod, '__spec__', None)
    if spec is not None:
        return spec

    name = mod.__name__
    loader = getattr(mod, '__loader__', None)
    filename = getattr(mod, '__file__', None)
    if loader is None:
        if name == '__main__':
            if not filename:
                return None
            # XXX Use SourceFileLoader.
            return None
        else:
            path = _get_path(mod)
            return _bootstrap._find_spec(name, path)
    else:
        if name == '__main__':
            # XXX Figure out the name for the spec?
            return None
        return _bootstrap.spec_from_loader(name, loader)


def _fix_module(mod):
    spec = _get_spec(mod)
    mod.__spec__ = spec
    mod.__loader__ = spec.loader if spec is not None else None
    # XXX Fix __pycache__?


def _fix_modules():
    # See _bootstrap.setup().
    module_type = type(sys)
    for name in sorted(sys.modules):
        module = sys.modules[name]
        if isinstance(module, module_type):
            _fix_module(module)


#################################################
# install

__original_import__ = None


def _install___import__():
    from . import __import__ as importlib___import__
    global __original_import__
    assert __original_import__ is None  # should only be called once...
    __original_import__ = _fixers.builtins.__import__
    _fixers.builtins.__import__ = importlib___import__


def inject():
    _fixers.inject_importlib('importlib2')
    _fixers.inject_importlib('importlib2._bootstrap')
    # XXX Tie this directly to "importlib"?
#    if name == _target + '._bootstrap':
#        # XXX Inject _boostrap into _frozen_importlib (if it exists)?
#        if not sys.modules.get('importlib._bootstrap'):
#            sys.modules['_frozen_importlib'] = bootstrap
    _fix_import_state()
    _fix_modules()


def install():
    with _locked():
        inject()
        _install___import__()
