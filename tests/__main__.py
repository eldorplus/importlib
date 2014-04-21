"""Run the full test suite.

Specifying the ``--builtin`` flag will run tests, where applicable, with
builtins.__import__ instead of importlib.__import__.

"""
from importlib2 import hook
from . import test_importlib


if __name__ == '__main__':
    hook.install()
    test_importlib.test_main()
