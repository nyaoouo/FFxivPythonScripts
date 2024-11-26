from nylib import ctype

from .utils import FileCommonHeader, File


class FileModel(FileCommonHeader):
    _size_ = 0XD4

    version = ctype.SField(ctype.c_uint32, 0X14)
    stack_memory_size = ctype.SField(ctype.c_uint32, 0X18)
    runtime_memory_size = ctype.SField(ctype.c_uint32, 0X1C)
    vertex_buffer_size = ctype.Field(ctype.c_uint32 * 3, 0X20)
    edge_geometry_vertex_buffer_size = ctype.Field(ctype.c_uint32 * 3, 0X2C)
    index_buffer_size = ctype.Field(ctype.c_uint32 * 3, 0X38)
    compressed_stack_memory_size = ctype.SField(ctype.c_uint32, 0X44)
    compressed_runtime_memory_size = ctype.SField(ctype.c_uint32, 0X48)
    compressed_vertex_buffer_size = ctype.Field(ctype.c_uint32 * 3, 0X4C)
    compressed_edge_geometry_vertex_buffer_size = ctype.Field(ctype.c_uint32 * 3, 0X58)
    compressed_index_buffer_size = ctype.Field(ctype.c_uint32 * 3, 0X64)
    stack_memory_offset = ctype.SField(ctype.c_uint32, 0X70)
    runtime_memory_offset = ctype.SField(ctype.c_uint32, 0X74)
    vertex_buffer_offset = ctype.Field(ctype.c_uint32 * 3, 0X78)
    edge_geometry_vertex_buffer_offset = ctype.Field(ctype.c_uint32 * 3, 0X84)
    index_buffer_offset = ctype.Field(ctype.c_uint32 * 3, 0X90)
    stack_data_block_index = ctype.SField(ctype.c_uint16, 0X9C)
    runtime_data_block_index = ctype.SField(ctype.c_uint16, 0X9E)
    vertex_buffer_data_block_index = ctype.Field(ctype.c_uint16 * 3, 0XA0)
    edge_geometry_vertex_buffer_data_block_index = ctype.Field(ctype.c_uint16 * 3, 0XA6)
    index_buffer_data_block_index = ctype.Field(ctype.c_uint16 * 3, 0XAC)
    stack_data_block_num = ctype.SField(ctype.c_uint16, 0XB2)
    runtime_data_block_num = ctype.SField(ctype.c_uint16, 0XB4)
    vertex_buffer_data_block_num = ctype.Field(ctype.c_uint16 * 3, 0XB6)
    edge_geometry_vertex_buffer_data_block_num = ctype.Field(ctype.c_uint16 * 3, 0XBC)
    index_buffer_data_block_num = ctype.Field(ctype.c_uint16 * 3, 0XC2)
    vertex_declaration_num = ctype.SField(ctype.c_uint16, 0XC8)
    material_num = ctype.SField(ctype.c_uint16, 0XCA)
    lod_num = ctype.SField(ctype.c_uint8, 0XCC)
    enable_index_buffer_streaming = ctype.SField(ctype.c_int8, 0XCD)
    enable_edge_geometry = ctype.SField(ctype.c_int8, 0XCE)
    compressed_block_size = ctype.Field(ctype.c_uint16 * 1, 0XD0)


class ModelFile(File[FileModel]):
    header_type = FileModel
