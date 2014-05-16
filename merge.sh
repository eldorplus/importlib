hg merge clean-cpython && \
  hg revert -r default REVISION pull-cpython.py
#  hg revert -r default importlib2/__init__.py
hg resolve -am
#hg commit -m 'Merge from clean-cpython.'
