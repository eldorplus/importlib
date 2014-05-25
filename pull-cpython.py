#!/usr/bin/env python3

import argparse
import os.path

from _util import load_version, read_py_version
from _util.os import pushd
from _util.repo import repo_revision, repo_root, repo_copytree, repo_copyfile


COPIED = {'Lib/importlib/': 'importlib2/',
          'Lib/test/test_importlib/': 'tests/test_importlib/',
          'Lib/test/lock_tests.py': 'tests/',
          'Lib/test/support/': 'tests/support/',
          'Lib/threading.py': 'tests/_fixers/',
          'Lib/py_compile.py': 'importlib2/_fixers/',
          'Lib/tokenize.py': 'importlib2/_fixers/',
          }

VERSION = load_version()


def save_revision(source, target, verbose=True, dryrun=False):
    rev = repo_revision(source)
    if verbose:
        print()
        print('==============================')
        print('REV: {}'.format(rev))
    if not dryrun:
        with pushd(target):
            with open(VERSION.PY_REVISION_FILE, 'w') as revfile:
                revfile.write(rev)
    return rev


def save_version(source, target, verbose=True, dryrun=False):
    # '{}.{}.{}'.format(*sys.version_info)
    py_version = read_py_version(source)
    if verbose:
        print()
        print('==============================')
        print('VERSION: {}'.format(py_version))
    if not dryrun:
        with pushd(target):
            with open(VERSION.PY_VERSION_FILE, 'w') as verfile:
                verfile.write(py_version)
    return py_version


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', dest='verbose', action='store_false',
                        default=True)
    parser.add_argument('--dryrun', action='store_true')
    parser.add_argument('source', metavar='SOURCEREPO')
    parser.add_argument('target', nargs='?', default='.',
                        metavar='TARGETREPO', help='(default ".")')
    args = parser.parse_args()

    if args.dryrun:
        args.verbose = True

    return args


if __name__ == '__main__':
    args = parse_args()

    sourcerepo = repo_root(args.source)
    targetrepo = repo_root(args.target)
    print('copying from {} to {}'.format(sourcerepo, targetrepo))

    for source in sorted(COPIED):
        target = COPIED[source]
        source = os.path.join(sourcerepo, source)
        target = os.path.join(targetrepo, target)
        if os.path.isdir(source):
            repo_copytree(source, target,
                          verbose=args.verbose,
                          dryrun=args.dryrun)
        else:
            repo_copyfile(source, target,
                          verbose=args.verbose,
                          dryrun=args.dryrun)

    save_revision(sourcerepo, targetrepo,
                  verbose=args.verbose,
                  dryrun=args.dryrun)
    save_version(sourcerepo, targetrepo,
                 verbose=args.verbose,
                 dryrun=args.dryrun)
