import io
import struct
from nylib import ctype

from .utils import FileCommonHeader, read_data_block, File


class CompressedDataBlockInfo(ctype.Struct):
    _size_ = 0X8
    compressed_data_block_offset = ctype.SField(ctype.c_uint32, 0X0)
    compressed_data_block_size = ctype.SField(ctype.c_uint16, 0X4)
    uncompressed_data_block_size = ctype.SField(ctype.c_uint16, 0X6)


class FileCompressedData(FileCommonHeader):
    _size_ = 0X18
    number_of_compressed_data_block_info = ctype.SField(ctype.c_uint32, 0X14)
    compressed_data_block_info = ctype.Field(CompressedDataBlockInfo * 1, 0X18)


COMPRESSED_DATA_BLOCK_INFO_OFFSET = 0x18  # FileCompressedData.compressed_data_block_info
COMPRESSED_DATA_BLOCK_INFO_SIZE = 0x8  # CompressedDataBlockInfo


class CompressedFile(File[FileCompressedData]):
    header_type = FileCompressedData

    def get_data_buffer(self, stream):
        data_pos = stream.tell()
        with io.BytesIO() as data_stream:
            for i in range(self.header.number_of_compressed_data_block_info):
                offset, compressed_size, uncompressed_size = struct.unpack_from(
                    f'<IHH', self.header_buffer,
                    COMPRESSED_DATA_BLOCK_INFO_OFFSET + i * COMPRESSED_DATA_BLOCK_INFO_SIZE
                )  # CompressedDataBlockInfo
                stream.seek(data_pos + offset)
                read_data_block(stream, data_stream)
            return bytearray(data_stream.getvalue())
