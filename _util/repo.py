import os
import os.path
import shutil
import subprocess

from .os import pushd


def _repo_cmd(cmd, dirname):
    # XXX sanitize dirname?
    with pushd(dirname):
        output = subprocess.check_output(cmd, shell=True)
    return output.decode().strip()


def repo_branch(dirname=None):
    if dirname is None:
        dirname = '.'
    cmd = 'hg branch'
    return _repo_cmd(cmd, dirname)


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
    if isinstance(filename, str):
        sfilename = filename
        tfilename = filename
    else:
        sfilename, tfilename = filename
    spath = os.path.join(source, sfilename)
    tpath = os.path.join(target, tfilename)

    if verbose:
        if sfilename == tfilename:
            print(sfilename)
        else:
            print('{} -> {}'.format(sfilename, tfilename))

    if not dryrun:
        try:
            os.makedirs(target)
        except OSError:
            pass
        shutil.copy2(spath, tpath)


def _copy_files(source, target, verbose, dryrun, filenames):
    source = os.path.abspath(source) + os.path.sep
    target = os.path.abspath(target) + os.path.sep
    if verbose:
        print('------------------------------')
        print(source)
        print('  to')
        print(target)
        print('------------------------------')
    for filename in filenames:
        _copy_file(filename, source, target, verbose, dryrun)


def repo_copytree(source, target, verbose=True, dryrun=False):
    filenames = repo_listdir(source)
    _copy_files(source, target, verbose, dryrun, filenames)


def repo_copyfile(source, target, verbose=True, dryrun=False):
    sfilename = os.path.basename(source)
    source = os.path.dirname(source)

    if target.endswith('/'):
        filenames = [sfilename]
    else:
        tfilename = os.path.basename(target)
        filenames = [(sfilename, tfilename)]
        target = os.path.dirname(target)

    _copy_files(source, target, verbose, dryrun, filenames)
