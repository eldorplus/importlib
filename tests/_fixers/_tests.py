from __future__ import unicode_literals, absolute_import


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
        print(EncodingTest.character)
