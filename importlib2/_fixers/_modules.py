from contextlib import contextmanager
import inspect
import os
import sys
import types


MODULE_TYPE = type(sys)


# destructive but idempotent
def fix_moduletype(bootstrap):
    if types.ModuleType is not MODULE_TYPE:
        # Already changed!
        return

    # Set a custom module type.
    class ModuleTypeMeta(type(MODULE_TYPE)):
        # Metaclass needed since we can't set __class__ on modules.
        def __instancecheck__(cls, obj):
            if super(ModuleTypeMeta, cls).__instancecheck__(obj):
                return True
            return isinstance(obj, MODULE_TYPE)
    class ModuleType(MODULE_TYPE):
        def __init__(self, name):
            super(ModuleType, self).__init__(name)
            self.__spec__ = None
            self.__loader__ = None
        def __repr__(self):
            return bootstrap._module_repr(self)
    ModuleTypeFixed = ModuleTypeMeta('ModuleType', (ModuleType,), {})

    #ModuleType.__module__ = bootstrap.__name__
    #bootstrap._new_module = ModuleType
    ModuleTypeFixed.__module__ = bootstrap.__name__
    bootstrap._new_module = ModuleTypeFixed


# destructive but idempotent
def inject_moduletype():
    import importlib2._bootstrap
    types.ModuleType = importlib2._bootstrap._new_module

    for module in sys.modules.values():
        # XXX How to get better __repr__?
        # Can't set __class__.
        #if module.__class__ is MODULE_TYPE:
        #    module.__class__ = types.ModuleType
        if not hasattr(module, '__spec__'):
            module.__spec__ = None
        if not hasattr(module, '__loader__'):
            module.__loader__ = None


#################################################
# module helpers

def _get_parent(mod):
    parent = mod.__name__.rpartition('.')[0]
    return sys.modules[parent] if parent else None


def _get_path(mod):
    parent = _get_parent(mod)
    if not parent:
        return sys.path
    else:
        return parent.__path__


# XXX Move to a classmethod of ModuleSpec?
def _copy_spec(spec, cls=None):
    if cls is None:
        from importlib2._bootstrap import _new_module as cls
    smsl = spec.submodule_search_locations
    copied = cls(spec.name, spec.loader,
                 origin=spec.origin,
                 loader_state=spec.loader_state,
                 is_package=(smsl is None))
    if smsl is not None:
        copied.submodule_search_locations.extend(smsl)
    copied.cached = spec.cached
    copied.has_location = spec.has_location
    return copied


def _get_spec(mod):
    from importlib2 import _bootstrap
    spec = getattr(mod, '__spec__', None)
    if spec is not None:
        if spec.__class__.__module__.startswith('importlib.'):
            # XXX Direct subclasses of importlib's ModuleSpec too?
            return _copy_spec(spec)
        else:
            return spec
    # Generate a new spec.
    # XXX Use _bootstrap._spec_from_module()?
    name = mod.__name__
    loader = getattr(mod, '__loader__', None)
    filename = getattr(mod, '__file__', None)
    if loader is None:
        if name == '__main__':
            if not filename:
                return None
            # XXX Use SourceFileLoader.
            spec = None
        else:
            path = _get_path(mod)
            spec = _bootstrap._find_spec(name, path)
    else:
        if name == '__main__':
            # XXX Figure out the name for the spec?
            spec = None
        else:
            spec = _bootstrap.spec_from_loader(name, loader)
    return spec


def _loader_class(loader):
    if isinstance(loader, type):
        return loader
    else:
        return loader.__class__


def _copy_loader(loader):
    cls = _loader_class(loader)
    instance = (loader is not cls)
    # Fix the class.
    if cls.__module__ == 'importlib._bootstrap':
        from importlib2 import _bootstrap
        cls = getattr(_bootstrap, cls.__name__)
    elif cls.__module__ == 'importlib.util':
        import importlib2.util
        cls = getattr(importlib2.util, cls.__name__)
    elif cls.__module__.startswith('importlib.'):
        # There shouldn't be any!
        raise NotImplementedError
    else:
        # Not an importlib loader, so don't copy!
        # XXX Replace importlib loaders in __bases__?
        return loader
    # Copy the loader.
    if not instance:
        copied = cls
    elif cls is not loader.__class__:
        # no-op!
        copied = loader
    else:
        argspec = inspect.getargspec(cls.__init__)
        kwargs = {getattr(loader, n) for n in argspec.args}
        copied = cls(**kwargs)
    return copied


def _get_loader(mod, spec=None):
    loader = getattr(mod, '__loader__', None)
    if loader is None:
        if spec is None:
            spec = getattr(mod, '__spec__', None)
            if spec is None:
                raise RuntimeError('{}: __spec__ should have been set already'
                                   .format(mod))
        loader = spec.loader
        if loader is None:
            from importlib2 import _bootstrap
            cls = _bootstrap._NamespaceLoader
            loader = cls.__new__(cls)
    assert loader is not None
    return _copy_loader(loader)


#################################################
# module fixers

def inject_module(mod):
    if mod.__class__ is not MODULE_TYPE:
        return
    if mod.__name__ == '__main__':
        # XXX __main__ might have a valid spec/loader...
        return

    spec = _get_spec(mod)
    if spec is None:
        raise RuntimeError('no spec found for {!r}'.format(mod))
    loader = _get_loader(mod, spec=spec)
    # Fix them up.
    if hasattr(mod, '__loader__') and spec.loader is mod.__loader__:
        # Keep them in sync.
        spec.loader = loader
    else:
        spec.loader = _copy_loader(spec.loader)
    # Set them.
    from importlib2 import _bootstrap
    mod.__spec__ = spec
    mod.__loader__ = loader
    # XXX Fix __pycache__?
    # XXX Fix any attributes in the module from importlib?


def inject_modules():
    # See _bootstrap.setup().
    for _, mod in sorted(sys.modules.items()):
        inject_module(mod)


def verify_module(mod, injected=True):
    if mod.__name__ == '__main__':
        return

    spec = getattr(mod, '__spec__', None)
    loader = getattr(mod, '__loader__', None)

    error = None
    if spec is None:
        error = '{!r} missing __spec__'
    elif loader is None:
        error = '{!r} missing __loader__'
    else:
        # __class__ is not writeable...
        #if mod.__class__ is MODULE_TYPE:
        #    error = '{!r} has wrong module type'
        if spec.__class__.__module__.startswith('importlib.'):
            error = '{!r} has wrong spec type'
        if _loader_class(loader).__module__.startswith('importlib.'):
            error = '{!r} has wrong loader type'

    if error is not None:
        raise RuntimeError(error.format(mod.__name__))


def verify_modules(injected=True):
    for _, mod in sys.modules.items():
        verify_module(mod, injected=injected)
