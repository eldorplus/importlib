import imp
import io
from itertools import zip_longest
import marshal


def format_bytes(data):
    for b in data:
        yield '{:02x}'.format(b)

def _w_long(x, size=4):
    mask = (2 << size * 8 - 1) - 1  # 0xFFFFFFFF
    return (int(x) & mask).to_bytes(4, 'little')


def _r_long(int_bytes):
    return int.from_bytes(int_bytes, 'little')


class PYC:

    @classmethod
    def from_raw(cls, data, path=None):
        rawmagic = data[0:4]
        rawtimestamp = data[4:8]
        rawsize = data[8:12]

        assert rawmagic[2:4] == b'\r\n', rawmagic
        magic = _r_long(rawmagic[:2])
        timestamp = _r_long(rawtimestamp)
        size = _r_long(rawsize)

        self = cls(magic, timestamp, size, data[12:], path)
        self._rawmagic = rawmagic
        self._rawtimestamp = rawtimestamp
        self._rawsize = rawsize
        return self

    @classmethod
    def from_file(cls, pycfile):
        if isinstance(pycfile, str):
            filename = pycfile
            with open(pycfile, 'rb') as pycfile:
                raw = pycfile.read()
        else:
            filename = getattr(pycfile, 'name', None)
            raw = pycfile.read()
        return cls.from_raw(raw, path=filename)

    def __init__(self, magic, timestamp, size, data, path=None):
        self.magic = magic
        self.timestamp = timestamp
        self.size = size
        self.data = data
        self.path = path

        self._rawmagic = None
        self._rawtimestamp = None
        self._rawsize = None

    def __repr__(self):
        parts = ', '.join('{}={!r}'.format(name, getattr(self, name))
                          for name in ('magic', 'timestamp', 'size', 'path'))
        return '{}({})'.format(self.__class__.__name__, parts)

    @property
    def rawmagic(self):
        try:
            return self._rawmagic
        except AttributeError:
            self._rawmagic = _w_long(self.magic, size=2) + b'\r\n'
            return self._rawmagic

    @property
    def rawtimestamp(self):
        try:
            return self._rawtimestamp
        except AttributeError:
            self._rawtimestamp = _w_long(self.timestamp)
            return self._rawtimestamp

    @property
    def rawsize(self):
        try:
            return self._rawsize
        except AttributeError:
            self._rawsize = _w_long(self.size)
            return self._rawsize

    def code(self):
        if self.rawmagic != imp.get_magic():
            return None
        else:
            return marshal.loads(self.data)

    def show(self, width=8, file=None, headeronly=False):
        for name in ('magic', 'timestamp', 'size'):
            value = getattr(self, name)
            raw = ' '.join(format_bytes(getattr(self, 'raw'+name)))
            line = '{:10} {:10} ({})'.format(name+':', value, raw)
            print(line, file=file)
        if headeronly:
            return
        print('', file=file)
        print('data:', file=file)
        size = len(self.data)
        i = 0
        while i < size:
            print(' '.join(format_bytes(self.data[i: i+width])), file=file)
            i += width


def dump_two(pyc1, pyc2, width=8, file=None, headeronly=False):
    lines1 = io.StringIO()
    lines2 = io.StringIO()
    pyc1.show(width=width, file=lines1, headeronly=headeronly)
    pyc2.show(width=width, file=lines2, headeronly=headeronly)
    lines1.seek(0)
    lines2.seek(0)

    fmt = ' {:%s} | {}' % (width * 2 + width - 1)
    print(fmt.format(pyc1.path or '', pyc2.path or ''))
    print(fmt.format('-' * 35, '-' * 35))
    for line1, line2 in zip_longest(lines1, lines2, fillvalue=''):
        print(fmt.format(line1.strip(), line2.strip()), file=file)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--header-only', dest='nodata', action='store_true')
    parser.add_argument('--width', type=int, default=8)
    parser.add_argument('pycfile')
    parser.add_argument('pycfile2', nargs='?')
    args = parser.parse_args()

    pyc = PYC.from_file(args.pycfile)

    if args.pycfile2:
        pyc2 = PYC.from_file(args.pycfile2)
        dump_two(pyc, pyc2, width=args.width, headeronly=args.nodata)
    else:
        pyc.show(width=args.width, headeronly=args.nodata)
