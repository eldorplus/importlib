importlib2
==========

A complete backport to 2.7 (and 3.x) of the ``importlib`` package from
Python 3.  Compatibility is intended to match only the latest public,
non-deprecated importlib API.

Note: This project is not yet released and the code base may be
unstable.  Currently the importlib tests all pass, but a few things
remain to be done before the initial release.

Note: Currently there is a problem under Python 3.2 with loading
modules from .pyc files.  However, this does not affect 2.7, which is
the main target for importlib2.


Usage
-----

You may use ``importlib2`` as you would any other module.  You may also
call ``importlib2.hook.install()`` to make Python use ``importlib2`` for
the import system.


API
---

See https://docs.python.org/dev/library/importlib.html.

Be aware that deprecated importlib APIs have not been backported.


Building and Installing
-----------------------

Use setup.py/pip/setuptools like normal.


Extra Files
-----------

``importlib2`` adds the following files to ``importlib`` (relative to
package's root directory):

* ``_fixers/`` - the code used to monkeypatch importlib2 at run-time
* ``_version/__init__.py`` - contains the ``importlib2`` version
   information
* ``_version/ORIGINAL_PY_VERSION`` - the major/minor/micro version of the
   cpython from which ``importlib2`` was most recently pulled
* ``_version/ORIGINAL_PY_REVISION`` - the revision of the cpython repo
   from which ``importlib2`` was most recently pulled
* ``_version/RELEASE`` - the ``importlib2`` release identifier relative
   to ``ORIGINAL_PY_VERSION`` (an increasing integer)
   from which ``importlib2`` was most recently pulled
* ``hook.py`` - the module used to set ``importlib2`` as Python's import
   system (not in the ``clean-cpython`` branch)


Tools
-----

Each is located in the project root.

* ``pull-cpython.py`` (only in the ``clean-cpython`` branch)
* ``tests/`` (run ``python -m tests``)


Main Branches
-------------

* ``clean-cpython`` - the relevant importlib files pulled from a cpython
   repo
* ``standalone-3.4`` - the files fixed so that the test suite passes
   using the Python interpreter built from the same cpython repo
* ``default`` - the files fixed to work under 2.7

Releases are made from the default branch.


Merging from cpython
--------------------

1. from the ``clean-cpython`` branch run ``pull-cpython.py``
2. commit the change
3. change to the ``standalone-3.4`` branch
4. merge from the ``clean-cpython`` branch
5. make any changes necessary to get the test suite to pass using
   the same cpython from which the files were most recently pulled
6. commit the changes (if any)
7. change to ``default``
8. merge from the ``standalone-3.4`` branch
9. make any changes necessary to get the test suite to pass using
   Python 2.7 (and 3.2)
10. commit the changes (if any)


Releasing
---------

<TBD>


Contributing
------------

Contributions are very welcome.  That said, my intent is that the
project start out stable and that the API mirror that of importlib as
closely as possible.  So if I've done things right there won't be much
need for contribution! :)

Regardless, I'm definitely interested in bug reports and I'd be glad to
take any feedback.  If you have a patch, definitely send a pull request.
If you have any suggestions on improving the importlib API, you may open
a ticket in the project tracker, but your best bet would be to open an
issue upstream on `Python's bug tracker`_ (add eric.snow and
brett.cannon to the nosy list).

.. _Python's bug tracker:: https://bugs.python.org


Reporting Issues and Feedback
-----------------------------

You may report bugs/suggestions/etc. issues to the project issue
tracker:

https://bitbucket.org/ericsnowcurrently/importlib2/issues

If that doesn't fit, you can either take the matter to the
import-sig@python.org `mailing list`_ or email me directly at
ericsnowcurrent@gmail.com.

.. _mailing list: https://mail.python.org/mailman/listinfo/import-sig


Acknowledgements
----------------

A special thanks goes to Brett Cannon who went through the painstaking
work of taking CPython's import machinery and turning it into a pure
Python library, importlib.  His efforts over the course of several years
bore fruit in Python 3.1 with the addition of importlib to the standard
library and culminated in the use of importlib as Python's import
machinery starting in Python 3.3.  Furthermore, without importlib's
thorough test suite importlib2 would have been essentially infeasible.
Thanks Brett!
