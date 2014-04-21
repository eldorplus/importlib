try:
    builtins = __import__('builtins')
except ImportError:
    builtins = __import__('__builtin__')


NAME = 'cpython'


#class ImportError(builtins.ImportError):
#    def __init__(self, msg, *args, **kwarg):
#        super(ImportError, self).__init__(msg)


def fix_imp(imp):
    if not hasattr(imp, 'extension_suffixes'):
        ext_suffixes = []
        imp.extension_suffixes = lambda: ext_suffixes
    if not hasattr(imp, '_fix_co_filename'):
        imp._fix_co_filename = lambda co, sp: None


def fix_sys(sys):
    if not hasattr(sys, 'implementation'):
        sys.implementation = type('SimpleNamespace', (), {})()
        sys.implementation.name = NAME
        sys.implementation.version = sys.version_info
        sys.implementation.hexversion = sys.hexversion
        sys.implementation.cache_tag = '{}-{}{}'.format(NAME, *sys.version_info[:2])


def fix_bootstrap(bootstrap):
#    bootstrap.NewImportError = ImportError
    pass


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
