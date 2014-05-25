import sys


def inject_py_compile():
    from . import py_compile
    sys.modules['py_compile'] = py_compile
