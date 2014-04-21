try:
    builtins = __import__('builtins')
except ImportError:
    builtins = __import__('__builtin__')
import sys


NAME = 'cpython'


class NewImportError(builtins.ImportError):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', None)
        self.path = kwargs.pop('path', None)
        super(ImportError, self).__init__(*args, **kwargs)


def fix_imp(_imp):
    sys.modules.setdefault('_imp', _imp)
    if not hasattr(_imp, 'extension_suffixes'):
        ext_suffixes = []
        _imp.extension_suffixes = lambda: ext_suffixes
    if not hasattr(_imp, '_fix_co_filename'):
        _imp._fix_co_filename = lambda co, sp: None


def fix_sys(sys):
    if not hasattr(sys, 'implementation'):
        sys.implementation = type('SimpleNamespace', (), {})()
        sys.implementation.name = NAME
        sys.implementation.version = sys.version_info
        sys.implementation.hexversion = sys.hexversion
        major, minor = sys.version_info[:2]
        sys.implementation.cache_tag = '{}-{}{}'.format(NAME, major, minor)


def fix_bootstrap(bootstrap):
    # XXX Inject _boostrap into _frozen_importlib (if it exists)?
    if not sys.modules.get('_frozen_importlib'):
        sys.modules['_frozen_importlib'] = bootstrap

    bootstrap.NewImportError = NewImportError

    class Module(type(sys)):
        def __init__(self, name):
            super(Module, self).__init__(name)
            self.__spec__ = None
            self.__loader__ = None
        def __repr__(self):
            return bootstrap._module_repr(self)
    Module.__module__ = bootstrap.__name__
    bootstrap._new_module = Module


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


def fix_builtins(builtins=builtins):
    pass
