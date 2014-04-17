"""Run the full test suite.

Specifying the ``--builtin`` flag will run tests, where applicable, with
builtins.__import__ instead of importlib.__import__.

"""
import test_importlib


if __name__ == '__main__':
    test_importlib.test_main()
