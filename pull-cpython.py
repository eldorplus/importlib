import argparse
from contextlib import contextmanager
import os
import os.path
import shutil
import subprocess
import sys


REVFILE = 'REVISION'

COPIED = {'Lib/importlib/': 'importlib2',
          'Lib/test/test_importlib/': 'tests/test_importlib',
          'Lib/test/lock_tests.py': 'tests',
          'Lib/test/support/': 'tests/support',
          }


# XXX Build into a DirStack class.
def pushd(dirname):
    cwd = os.getcwd()
    os.chdir(dirname)
    @contextmanager
    def restore():
        try:
            yield cwd
        finally:
            os.chdir(cwd)
    return restore()


def _repo_cmd(cmd, dirname):
    # XXX sanitize dirname?
    with pushd(dirname):
        output = subprocess.check_output(cmd, shell=True)
    return output.decode().strip()


def repo_root(dirname=None):
    if dirname is None:
        dirname = '.'
    cmd = 'hg root'
    return _repo_cmd(cmd, dirname)


def repo_listdir(dirname):
    cmd = 'hg status -n -c .'
    output = _repo_cmd(cmd, dirname)
    return output.splitlines()


def repo_revision(dirname):
    cmd = 'hg id -i'
    return _repo_cmd(cmd, dirname)


def _copy_file(filename, source, target, verbose, dryrun):
    sfilename = os.path.join(source, filename)
    tfilename = os.path.join(target, filename)
    if verbose:
        print(filename)
    if not dryrun:
        try:
            os.makedirs(target)
        except OSError:
            pass
        shutil.copy2(sfilename, tfilename)


def _copy_files(source, target, verbose, dryrun, filenames=None):
    source = os.path.abspath(source) + os.path.sep
    target = os.path.abspath(target) + os.path.sep
    if verbose:
        print('------------------------------')
        print(source)
        print('  to')
        print(target)
        print('------------------------------')
    if filenames is None:
        filenames = repo_listdir(source)
    for filename in filenames:
        _copy_file(filename, source, target, verbose, dryrun)


def repo_copytree(source, target, verbose=True, dryrun=False):
    _copy_files(source, target, verbose, dryrun)


def repo_copyfile(source, target, verbose=True, dryrun=False):
    filenames = (os.path.basename(source),)
    _copy_files(os.path.dirname(source), target, verbose, dryrun, filenames)


def save_revision(source, target, verbose=True, dryrun=False):
    rev = repo_revision(source)
    if verbose:
        print()
        print('==============================')
        print('REV: {}'.format(rev))
    if not dryrun:
        with pushd(target):
            with open(REVFILE, 'w') as revfile:
                revfile.write(rev)
    return rev


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
