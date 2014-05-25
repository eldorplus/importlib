#!/usr/bin/env python3

import subprocess


BIN = "3to2"

DEFAULTS =['importlib2',
           #'tests',
           #'tests/support',
           'tests/test_importlib',
           'tests/lock_tests.py',
           ]

DISABLED = [
        #'annotations',
        #'bitlength',
        #'bool',
        'bytes',
        'classdecorator',
        #'collections',
        'dctsetcomp',
        #'division',
        'except',
        'features',
        #'fullargspec',
        'funcattrs',
        'getcwd',
        'imports',
        'imports2',
        #'input',
        #'int',
        #'intern',
        #'itertools',
        #'kwargs',
        #'memoryview',
        #'metaclass',
        'methodattrs',
        #'newstyle',
        #'next',
        'numliterals',
        'open',
        'print',
        #'printfunction',
        #'raise',
        'range',
        #'reduce',
        'setliteral',
        'str',
        #'super',
        #'throw',
        #'unittest',
        #'unpacking',
        'with',
        ]

if __name__ == '__main__':
    import sys
    dirs = sys.argv[1:] or DEFAULTS
    cmd = '{} {} {}'.format(BIN,
                            ' '.join('-x '+n for n in DISABLED),
                            ' '.join(dirs))
    print('==============')
    print(cmd)
    print('==============')
    subprocess.call(cmd, shell=True)

#if [ $# -eq 0 ]; then
#    DIRS= importlib2 test
#else
#    DIRS= $@
#fi
#
#CMD="3to2 -x str -x bytes -x with -x funcattrs -x except -x range -x methodattrs -x print -x numliterals -x dctsetcomp -x classdecorator -x setliteral -x features $DIRS"
#
#echo ==============
#echo $CMD
#echo ==============
#exec $CMD
