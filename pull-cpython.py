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
    return output.strip()


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


def repo_copytree(source, target, verbose=True, dryrun=False):
    source = os.path.abspath(source) + os.path.sep
    target = os.path.abspath(target) + os.path.sep
    if verbose:
        print('------------------------------')
        print(source)
        print('  to')
        print(target)
        print('------------------------------')
    for filename in repo_listdir(source):
        sfilename = os.path.join(source, filename)
        tfilename = os.path.join(target, filename)
        if verbose:
            print(filename)
        if not dryrun:
            try:
                os.makedirs(os.path.dirname(tfilename))
            except OSError:
                pass
            shutil.copy2(sfilename, tfilename)


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
    parser.add_argument('source')
    parser.add_argument('target', nargs='?', default='.')
    args = parser.parse_args()

    if args.dryrun:
        args.verbose = True

    return args


if __name__ == '__main__':
    args = parse_args()

    sourcerepo = repo_root(args.source)
    targetrepo = repo_root(args.target)

    for source, target in COPIED.items():
        source = os.path.join(sourcerepo, source)
        target = os.path.join(targetrepo, target)
        repo_copytree(source, target,
                      verbose=args.verbose,
                      dryrun=args.dryrun)

    save_revision(sourcerepo, targetrepo,
                  verbose=args.verbose,
                  dryrun=args.dryrun)
