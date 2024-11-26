import struct
import typing
import zlib
from typing import IO, TypeVar, TYPE_CHECKING, Any
from nylib import ctype

if TYPE_CHECKING:
    from ..indexfile import FileInfo

BLOCK_INFO = struct.Struct(f'<IIII')
BLOCK_INFO_SIZE = BLOCK_INFO.size
BLOCK_PADDING = 0x80
COMPRESSION_THRESHOLD = 0x7D00


class FileCommonHeader(ctype.Struct):
    _size_ = 0X14

    size = ctype.SField(ctype.c_uint32, 0X0)
    type = ctype.SField(ctype.c_uint32, 0X4)
    file_size = ctype.SField(ctype.c_uint32, 0X8)
    number_of_block = ctype.SField(ctype.c_uint32, 0XC)
    used_number_of_block = ctype.SField(ctype.c_uint32, 0X10)


FileCommonHeader_T = TypeVar("FileCommonHeader_T", bound=FileCommonHeader)


def read_data_block(src: IO[bytes], dst: IO[bytes]):
    size, version, compressed_size, uncompressed_size = BLOCK_INFO.unpack(src.read(BLOCK_INFO_SIZE))  # CompressionBlockInfo16
    assert size == BLOCK_INFO_SIZE
    is_compressed = compressed_size < COMPRESSION_THRESHOLD
    block_size = uncompressed_size if is_compressed else compressed_size
    if is_compressed and ((block_size + BLOCK_INFO_SIZE) % BLOCK_PADDING) != 0:
        block_size += BLOCK_PADDING - ((block_size + BLOCK_INFO_SIZE) % BLOCK_PADDING)
    buffer = src.read(block_size)
    if is_compressed:
        assert uncompressed_size == dst.write(zlib.decompress(buffer, -15)), RuntimeError("Inflated block does not match indicated size")
    else:
        dst.write(buffer)


class File(typing.Generic[FileCommonHeader_T]):
    header_type: typing.Type[FileCommonHeader_T] = FileCommonHeader
    header: FileCommonHeader_T
    info: 'FileInfo'
    data: Any

    def __init__(self, info: 'FileInfo', header_data: bytes):
        self.info = info
        self.header_buffer = bytearray(header_data)
        self.header = ctype.cdata_from_buffer(self.header_buffer, self.header_type)
        self.data_size = self.header.file_size - self.header.size
        self._data_buffer: bytearray | None = None

    def get_data_buffer(self, stream: IO) -> bytearray:
        return bytearray(stream.read(self.data_size))

    @property
    def data_buffer(self) -> bytearray:
        if self._data_buffer is None:
            self._data_buffer = self.get_data_buffer(self.data_stream)
        return self._data_buffer

    @property
    def data_stream(self) -> IO:
        stream = self.info.dir.index.pack.get_data_stream(self.info.info.data_file_id)
        stream.seek(self.info.offset + self.header.size)
        return stream
