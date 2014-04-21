from __future__ import absolute_import, division, print_function, unicode_literals

from contextlib import contextmanager
import os
import sys

from . import _bootstrap
from ._containers import SequenceProxy, MappingProxy


@contextmanager
def _locked():
    _bootstrap._imp.acquire_lock()
    try:
        yield
    finally:
        _bootstrap._imp.release_lock()


class MetapathWrapper(SequenceProxy):

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

    def __init__(self, finders):
        super(MetapathWrapper, self).__init__(finders, readonly=False)
        self._finders = finders
        self._backportfinder = BackportFinder(finders)

        self._old = self._remove_old_defaults(finders)
        self._add_default_finders(finders)

    def __len__(self):
        return super(MetapathWrapper, self).__len__() + 1

    def __iter__(self):
        yield self._backportfinder
        for finder in self._finders:
            yield finder

    def __getitem__(self, index):
        if index == 0:
            return self._backportfinder
        else:
            return super(MetapathWrapper, self).__getitem__(index - 1)

    def __setitem__(self, index, value):
        if index == 0:
            raise IndexError('cannot replace backport finder')
            # XXX Or redirect to index 1.
        super(MetapathWrapper, self).__setitem__(index - 1, value)

    def __delitem__(self, index):
        if index == 0:
            raise IndexError('cannot remove backport finder')
            # XXX Or redirect to index 1.
        super(MetapathWrapper, self).__delitem__(index - 1)

    @property
    def backportfinder(self):
        return self._backportfinder

    def insert(self, index, value):
        if index == 0:
            index = 1
        super(MetapathWrapper, self).insert(index - 1, value)


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

    def __getattr__(self, name):
        # XXX special-case namespace packages?
        return getattr(self._spec.loader, name)

    def load_module(self, name):
        if name != self._spec.name:
            raise ImportError('wrong name: expected {!r}, got {!r}'
                              .format(self._spec.name, name))
        return _bootstrap._SpecMethods(self._spec).load()


class PathHooksWrapper(SequenceProxy):

    @classmethod
    def _get_old_defaults(cls, hooks):
        # The only hooks from _bootstrap come from FileFinder.
        oldhooks = []
        for hook in hooks:
            if hook.__module__ == '_frozen_importlib':
                oldhooks.append(hook)
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
        super(PathHooksWrapper, self).__init__(hooks, readonly=False)
        self._hooks = hooks

        self._old = self._remove_old_defaults(hooks)
        self._add_default_hooks(hooks)


def install():
    with _locked():
        sys.path_hooks = PathHooksWrapper(sys.path_hooks)
        # XXX sys.path_importer_cache too?
        sys.meta_path = MetapathWrapper(sys.meta_path)
