from __future__ import absolute_import, division, print_function, unicode_literals

from contextlib import contextmanager
import os
import sys

from . import _bootstrap
#from ._containers import SequenceProxy, MappingProxy


@contextmanager
def _locked():
    _bootstrap._imp.acquire_lock()
    try:
        yield
    finally:
        _bootstrap._imp.release_lock()


# Can't use SequenceProxy for 2.7/3.2. :(
class MetapathWrapper(list):

    @classmethod
    def _get_old_defaults(cls, finders):
        # The only metapath finder classes in _boostrap are defaults.
        oldfinders = []
        for finder in finders:
            modname = getattr(finder, '__module__',
                              finder.__class__.__module__)
            if modname == '_frozen_importlib':
                oldfinders.append(finder)
        return oldfinders

    @classmethod
    def _remove_old_defaults(cls, finders):
        # Remove 3.4+ defaults from sys.meta_path.
        oldfinders = cls._get_old_defaults(finders)
        for finder in oldfinders:
            if isinstance(finders, MetapathWrapper):
                super(MetapathWrapper, finders).remove(finder)
            else:
                finders.remove(finder)
        return oldfinders

    @classmethod
    def _add_default_finders(cls, finders):
        # See _bootstrap._install().
        finders.append(_bootstrap.BuiltinImporter)
        finders.append(_bootstrap.FrozenImporter)
        if os.name == 'nt':
            finders.append(_bootstrap.WindowsRegistryFinder)
        finders.append(_bootstrap.PathFinder)

    def __new__(cls, finders):
        if isinstance(finders, MetapathWrapper):
            return finders
        else:
            return super(MetapathWrapper, cls).__new__(cls, finders)

    def __init__(self, finders):
        if hasattr(self, '_finders'):
            # Only run __init__ once.
            return
        super(MetapathWrapper, self).__init__(finders)
        self._finders = finders
        self._backportfinder = BackportFinder(finders)
        super(MetapathWrapper, self).insert(0, self._backportfinder)

        self._old = self._remove_old_defaults(self)
        self._add_default_finders(self)

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            raise TypeError('slicing not supported')
        elif index < 0:
            raise TypeError('negative index not supported')
        elif index == 0:
            raise IndexError('cannot replace backport finder')
            # XXX Or redirect to index 1.
        else:
            super(MetapathWrapper, self).__setitem__(index, value)

    def __delitem__(self, index):
        if isinstance(index, slice):
            raise TypeError('slicing not supported')
        elif index < 0:
            raise TypeError('negative index not supported')
        elif index == 0:
            raise IndexError('cannot remove backport finder')
            # XXX Or redirect to index 1.
        else:
            super(MetapathWrapper, self).__delitem__(index)

    @property
    def backportfinder(self):
        return self._backportfinder

    def insert(self, index, value):
        if isinstance(index, slice):
            raise TypeError('slicing not supported')
        elif index < 0:
            raise TypeError('negative index not supported')
        if index == 0:
            # XXX Too sneaky?
            index = 1
        super(MetapathWrapper, self).insert(index, value)

    def remove(self, value):
        if value is self._backportfinder:
            raise TypeError('remove() not supported')
        else:
            super(MetapathWrapper, self).remove(value)

    def pop(self, *args, **kwargs):
        raise TypeError('pop() not supported')

    def reverse(self, *args, **kwargs):
        raise TypeError('reverse() not supported')

    def sort(self, *args, **kwargs):
        raise TypeError('sort() not supported')


class BackportFinder(object):

    def __init__(self, finders):
        self.finders = finders

    def find_module(self, name, path=None):
        spec = _bootstrap._find_spec(name, path, meta_path=self.finders)
        if spec is None:
            return None
        else:
            return BackportLoader(spec)


class BackportLoader(object):

    # XXX create_module() -> subclass of ModuleType?

    def __init__(self, spec):
        self._spec = spec

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self._spec)

    def __str__(self):
        return str(self._spec.loader)

    def __getattr__(self, name):
        # XXX special-case namespace packages?
        return getattr(self._spec.loader, name)

    def __eq__(self, other):
        try:
            other_spec = other.spec
        except AttributeError:
            # other must be a loader.
            return self._spec.loader == other
        else:
            return self._spec == other_spec

    def __ne__(self, other):
        return not (self == other)

    @property
    def spec(self):
        return self._spec

    def load_module(self, name):
        if name != self._spec.name:
            raise ImportError('wrong name: expected {!r}, got {!r}'
                              .format(self._spec.name, name))
        return _bootstrap._SpecMethods(self._spec).load()


# Can't use SequenceProxy for 2.7/3.2. :(
class PathHooksWrapper(list):

    @classmethod
    def _get_old_defaults(cls, hooks):
        # The only hooks from _bootstrap come from FileFinder.
        oldhooks = []
        for hook in hooks:
            if hook.__module__ == '_frozen_importlib':
                oldhooks.append(hook)
        # XXX Include imp.NullImporter?
        return oldhooks

    @classmethod
    def _remove_old_defaults(cls, hooks):
        # Remove 3.4+ defaults from sys.path_hooks.
        oldhooks = cls._get_old_defaults(hooks)
        for hook in oldhooks:
            hooks.remove(hook)
        return oldhooks

    @classmethod
    def _add_default_hooks(cls, hooks):
        # See _bootstrap._install().
        supported_loaders = _bootstrap._get_supported_file_loaders()
        hook = _bootstrap.FileFinder.path_hook(*supported_loaders)
        hooks.extend([hook])

    def __init__(self, hooks):
        super(PathHooksWrapper, self).__init__(hooks)
        self._hooks = hooks

        self._old = self._remove_old_defaults(self)
        self._add_default_hooks(self)


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
            # XXX Figure out the name for the spec.
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

def _install___import__():
    from ._fixers import builtins
    _import = builtins.__import__
    def __import__(name, *args, **kwargs):
        print(name)
        return _import(name, *args, **kwargs)
    builtins.__import__ = __import__


def _install_finder():
    sys.path_hooks = PathHooksWrapper(sys.path_hooks)
    # XXX sys.path_importer_cache too?
    sys.meta_path = MetapathWrapper(sys.meta_path)


def install():
    with _locked():
        #_install___import__()
        _install_finder()
        sys.path_importer_cache.clear()
        _fix_modules()
