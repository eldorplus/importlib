from __future__ import absolute_import, division, print_function, unicode_literals

from collections import MutableSequence, MutableMapping


def _clear(container):
    copied = container.__class__(container)
    try:
        clear = container.clear
    except AttributeError:
        for _ in copied:
            container.pop()
    else:
        clear()
    return copied


def _inject(container, values, clear=False):
    if clear:
        copied = _clear(container)
    else:
        copied = None
    for i, value in enumerate(values):
        container.insert(i, value)
    return copied


class _Proxy(object):

    def __init__(self, raw, readonly=True):
        self._raw = raw
        self._readonly = readonly

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self._raw)

    @property
    def readonly(self):
        return self._readonly


class _ContainerProxy(_Proxy):

    def __len__(self):
        return len(self._raw)

    def __getitem__(self, key_or_index):
        return self._raw[key_or_index]

    def __setitem__(self, key_or_index, value):
        if self._readonly:
            raise TypeError('readonly proxy')
        self._raw[key_or_index] = value

    def __delitem__(self, key_or_index):
        if self._readonly:
            raise TypeError('readonly proxy')
        del self._raw[key_or_index]


class SequenceProxy(_ContainerProxy, MutableSequence):

    def insert(self, index, value):
        self._raw.insert(index, value)


class MappingProxy(_ContainerProxy, MutableMapping):

    def __iter__(self):
        for key in self._map:
            yield key
