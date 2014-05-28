from __future__ import unicode_literals, absolute_import

import unittest


skip_deprecated = unittest.skip('deprecated API')


def _disable_test(mod, case, name=None):
    cls = getattr(mod, case)
    if name is None:
        cls = skip_deprecated(cls)
        setattr(mod, case, cls)
    else:
        method = getattr(cls, name)
        if hasattr(method, 'im_func'):
            method = method.im_func
        setattr(cls, name, skip_deprecated(method))


def fix_test_source_encodings():
    from tests.test_importlib.source.test_source_encoding import EncodingTest

    try:
        unicode
    except NameError:
        pass
    else:
        EncodingTest.variable = 'spam'
        EncodingTest.source_line = ("{0} = '{1}'\n"
                                    ).format(EncodingTest.variable,
                                             EncodingTest.character)
