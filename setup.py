from distutils.core import setup
import os.path

import _util
_util.verify_release_branch()

import importlib2


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


#################################################
# Define the package metadata.

NAME = 'importlib2'  # both for the package and the distribution
VERSION = importlib2.__version__
AUTHOR = 'Eric Snow'
EMAIL = 'ericsnowcurrently@gmail.com'
URL = 'https://bitbucket.org/ericsnowcurrently/importlib2/'
LICENSE = 'New BSD License'
SUMMARY = 'A backport of the Python 3 importlib package.'
# DESCRIPTION is dynamically built below.
KEYWORDS = ''
PLATFORMS = []
CLASSIFIERS = [
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        #'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        ]

with open(os.path.join(PROJECT_ROOT, 'README')) as readme_file:
     DESCRIPTION = readme_file.read()


#################################################
# Set up packages.

PACKAGES = ['importlib2']


#################################################
# Pull it all together.

kwargs = {'name': NAME,
          'version': VERSION,
          'author': AUTHOR,
          'author_email': EMAIL,
          #'maintainer': MAINTAINER,
          #'maintainer_email': MAINTAINER_EMAIL,
          'url': URL,
          #'download_url': DOWNLOAD,
          'license': LICENSE,
          'description': SUMMARY,
          'long_description': DESCRIPTION,

          'keywords': KEYWORDS,
          'platforms': PLATFORMS,
          'classifiers': CLASSIFIERS,

          'packages': PACKAGES,
          }

for key in list(kwargs):
    if not kwargs[key]:
        del kwargs[key]


if __name__ == '__main__':
    setup(**kwargs)
