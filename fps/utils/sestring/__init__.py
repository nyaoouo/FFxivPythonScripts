import enum
import io
import struct
import typing

from .define import MacroType, MACRODEFPARAM

_int_masks = [
    1 << 3,
    1 << 2,
    1 << 1,
    1 << 0,
]

_small_i8 = struct.Struct('b')
_small_u8 = struct.Struct('B')
_big_i32 = struct.Struct('>i')
BIO_T = typing.IO[bytes]


def peek_io(io: BIO_T, size: int) -> bytes:
    pos = io.tell()
    data = io.read(size)
    io.seek(pos)
    return data


def write_integer(buf: BIO_T, value: int, cutoff=0xCF):
    if -1 < value < cutoff:
        buf.write(_small_i8.pack(value))
        return
    res = bytearray(1)
    flag = 0xff
    for _mask, _v in zip(_int_masks, _big_i32.pack(value)):
        if _v:
            res.append(_v)
        else:
            flag ^= _mask
    res[0] = flag - 1
    buf.write(res)


def write_string(buf: BIO_T, value: 'str|Macro|SeString', encoding='utf-8'):
    buf.write(b'\xff')
    b = value.encode(encoding)
    write_integer(buf, len(b))
    buf.write(b)


def write_data(buf: BIO_T, d, encoding='utf-8'):
    if isinstance(d, MACRODEFPARAM):
        buf.write(_small_u8.pack(d.value))
    elif isinstance(d, enum.Enum):
        raise TypeError(f'unsupported type: {type(d)}')
    elif isinstance(d, int):
        write_integer(buf, d)
    elif isinstance(d, (str, Macro, SeString)):
        write_string(buf, d, encoding)
    elif isinstance(d, bytes):
        buf.write(d)
    else:
        raise TypeError(f'unsupported type: {type(d)}')


def read_integer(buf: BIO_T) -> int:
    marker = buf.read(1)[0]
    if marker < 0xF0: return marker - 1
    marker += 1
    buffer = bytearray(4)
    for i, mask in enumerate(_int_masks):
        if marker & mask:
            buffer[i] = buf.read(1)[0]
    return _big_i32.unpack(buffer)[0]


def read_data(buf: BIO_T, encoding='utf-8') -> 'str|int|Macro|SeString':
    marker = buf.read(1)[0]
    if marker == 0xFF:
        size = read_integer(buf)
        return SeString.read(buf, encoding, size)
    if marker < 0xD0:
        return marker - 1
    if marker < 0xF0:
        return MACRODEFPARAM(marker)
    buf.seek(-1, io.SEEK_CUR)
    return read_integer(buf)


class Macro:
    def __init__(self, macro_type: MacroType, *args: 'str|int|SeString'):
        self.macro_type = macro_type
        self.args = list(args)

    def write(self, buf: BIO_T, encoding='utf-8'):
        buf_ = io.BytesIO()
        for arg in self.args:
            write_data(buf_, arg, encoding)
        buf_ = buf_.getbuffer()
        buf.write(bytes([MacroType.BEGIN, self.macro_type]))
        write_integer(buf, buf_.nbytes)
        buf.write(buf_)
        buf.write(_small_u8.pack(MacroType.END))

    def encode(self, encoding='utf-8') -> bytes:
        buf = io.BytesIO()
        self.write(buf, encoding)
        return buf.getvalue()

    @classmethod
    def read(cls, buf: BIO_T, encoding='utf-8') -> 'Macro':
        assert buf.read(1)[0] == MacroType.BEGIN
        obj = cls(MacroType(buf.read(1)[0]))
        end = read_integer(buf) + buf.tell()
        while buf.tell() < end:
            obj.args.append(read_data(buf, encoding))
        assert buf.read(1)[0] == MacroType.END
        return obj

    def __repr__(self):
        return f'<Macro {self.macro_type.name}({", ".join(map(repr, self.args))})>'


class SeString:
    args: typing.List['str|Macro']

    def __init__(self, *args: 'str|Macro'):
        self.args = list(args)

    def write(self, buf: BIO_T, encoding='utf-8'):
        for arg in self.args:
            if isinstance(arg, str):
                write_string(buf, arg, encoding)
            elif isinstance(arg, Macro):
                arg.write(buf, encoding)
            else:
                raise TypeError(f'unsupported type: {type(arg)}')

    def encode(self, encoding='utf-8') -> bytes:
        buf = io.BytesIO()
        self.write(buf, encoding)
        return buf.getvalue()

    def __add__(self, other: 'SeString|Macro|str') -> 'SeString':
        if isinstance(other, SeString):
            return SeString(*self.args, *other.args)
        return SeString(*self.args, other)

    def __iadd__(self, other):
        if isinstance(other, SeString):
            self.args.extend(other.args)
        else:
            self.args.append(other)
        return self

    def __getitem__(self, item):
        return self.args[item]

    def __getattr__(self, item):
        return getattr(self.args, item)

    def __str__(self):
        return ''.join(map(str, self.args))

    def __repr__(self):
        return f'<SeString: {self}>'

    def split(self, splitter: str, maxsplit: int = -1):
        res = [SeString()]
        for i, e in enumerate(self.args):
            if isinstance(e, (SeString, Macro)):
                res[-1].append(e)
                continue
            *splits, last = e.split(splitter, maxsplit)
            if splits:
                for split in splits:
                    res[-1].append(split)
                    res.append(SeString())
            res[-1].append(last)
            if maxsplit > 0:
                maxsplit -= len(splits)
                if maxsplit <= 0:
                    res[-1].extend(self[i + 1:])
                    break
        return res

    @classmethod
    def loads(cls, s: bytes, encoding='utf-8') -> 'SeString':
        return cls.read(io.BytesIO(s), encoding)

    @classmethod
    def read(cls, buf: BIO_T, encoding='utf-8', size: int = -1) -> 'SeString':
        obj = cls()
        end = buf.tell() + size if size >= 0 else -1
        b = io.BytesIO()
        while end < 0 or buf.tell() < end:
            c = buf.read(1)
            if not c: break
            if c[0] == MacroType.BEGIN:
                if b.tell():
                    obj.args.append(b.getvalue().decode(encoding))
                buf.seek(-1, io.SEEK_CUR)
                obj.args.append(Macro.read(buf, encoding))
                b = io.BytesIO()
                continue
            b.write(c)
        if b.tell():
            obj.args.append(b.getvalue().decode(encoding))
        return obj
