from __future__ import absolute_import

import os.path as os_path
import re
import sys

from .repo import repo_branch


UTIL_ROOT = os_path.abspath(os_path.dirname(__file__))
PROJECT_ROOT = os_path.dirname(UTIL_ROOT)

VER_RE = re.compile(r'#define PY_VERSION\s+"(\d\.\d+\.\d+).*"')


def load_version():
    pkg_root = os_path.join(PROJECT_ROOT, 'importlib2')
    sys.path.insert(0, pkg_root)
    import _version
    del sys.modules[_version.__name__]
    sys.path.remove(pkg_root)
    return _version


def read_py_version(source):
    filename = os_path.join(source, 'Include', 'patchlevel.h')
    with open(filename) as verfile:
        for line in verfile:
            match = VER_RE.match(line)
            if not match:
                continue
            version, = match.groups()
            return version.strip()
        else:
            raise RuntimeError('unable to find Python version')


def verify_release_branch(_release_prefix='release-'):
    branch = repo_branch()
    if branch != 'default' and not branch.startswith(_release_prefix):
        raise RuntimeError('not a release branch: {!r}'.format(branch))
