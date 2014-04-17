import os
from importlib import import_module
from distutils.core import setup

from importlib2 import __version__


basedir = os.path.abspath(os.path.dirname(__file__) or '.')


# required data

package_name = 'importlib2'
summary = 'A backport of the Python 3 importlib package.'
with open(os.path.join(basedir, 'README')) as readme_file:
     description = readme_file.read()
project_url = 'https://bitbucket.org/ericsnowcurrently/importlib2/'

# dymanically generated data

version = '.'.join(str(val) for val in __version__)


# set up packages

packages = ['importlib2']


# other data

classifiers = [
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        #'License :: OSI Approved :: Apache Software License',
        #'License :: OSI Approved :: BSD License',
        #'License :: OSI Approved :: MIT License',
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


if __name__ == '__main__':
    setup (
            name=package_name,
            version=version,
            author='Eric Snow',
            author_email='ericsnowcurrently@gmail.com',
            url=project_url,
            license='New BSD License',
            description=summary,
            long_description=description,
            classifiers=classifiers,
            packages=packages,
            )
