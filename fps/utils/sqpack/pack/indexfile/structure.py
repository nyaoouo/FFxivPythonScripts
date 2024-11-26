from nylib import ctype


class VersionInfo(ctype.Struct):
    _size_ = 0X400
    magic_str = ctype.SField(ctype.c_char_zt[8], 0X0)
    platform_id = ctype.SField(ctype.c_uint8, 0X8)
    size = ctype.SField(ctype.c_uint32, 0XC)
    version = ctype.SField(ctype.c_uint32, 0X10)
    type = ctype.SField(ctype.c_uint32, 0X14)
    date = ctype.SField(ctype.c_uint32, 0X18)
    time = ctype.SField(ctype.c_uint32, 0X1C)
    region_id = ctype.SField(ctype.c_uint32, 0X20)
    language_id = ctype.SField(ctype.c_uint32, 0X24)
    self_hash = ctype.Field(ctype.c_uint8 * 64, 0X3C0)


class IndexFileInfo(ctype.Struct):
    _size_ = 0X400
    size = ctype.SField(ctype.c_uint32, 0X0)
    version = ctype.SField(ctype.c_uint32, 0X4)
    index_data_offset = ctype.SField(ctype.c_uint32, 0X8)
    index_data_size = ctype.SField(ctype.c_uint32, 0XC)
    index_data_hash = ctype.Field(ctype.c_uint8 * 64, 0X10)
    number_of_data_file = ctype.SField(ctype.c_uint32, 0X50)
    synonym_data_offset = ctype.SField(ctype.c_uint32, 0X54)
    synonym_data_size = ctype.SField(ctype.c_uint32, 0X58)
    synonym_data_hash = ctype.Field(ctype.c_uint8 * 64, 0X5C)
    empty_block_data_offset = ctype.SField(ctype.c_uint32, 0X9C)
    empty_block_data_size = ctype.SField(ctype.c_uint32, 0XA0)
    empty_block_data_hash = ctype.Field(ctype.c_uint8 * 64, 0XA4)
    dir_index_data_offset = ctype.SField(ctype.c_uint32, 0XE4)
    dir_index_data_size = ctype.SField(ctype.c_uint32, 0XE8)
    dir_index_data_hash = ctype.Field(ctype.c_uint8 * 64, 0XEC)
    index_type = ctype.SField(ctype.c_uint32, 0X12C)
    self_hash = ctype.Field(ctype.c_uint8 * 64, 0X3C0)


class DirectoryIndexInfo(ctype.Struct):
    _size_ = 0X10
    dir_hash = ctype.SField(ctype.c_uint32, 0X0)
    offset = ctype.SField(ctype.c_uint32, 0X4)
    size = ctype.SField(ctype.c_uint32, 0X8)


class SynonymTableElem_Hash32(ctype.Struct):
    _size_ = 0X100

    hash_hoge = ctype.SField(ctype.c_uint32, 0X0)
    reserve = ctype.SField(ctype.c_uint32, 0X4)
    reserved = ctype.BField(ctype.c_uint32, 1, 0X8)
    data_file_id = ctype.BField(ctype.c_uint32, 3, 0X8)
    block_offset = ctype.BField(ctype.c_uint32, 28, 0X8)
    synonym_index = ctype.SField(ctype.c_uint32, 0XC)
    path = ctype.SField(ctype.c_char[240], 0X10)


class SynonymTableElem_Hash64(ctype.Struct):
    _size_ = 0X100

    hash_hoge = ctype.SField(ctype.c_uint64, 0X0)
    reserved = ctype.BField(ctype.c_uint32, 1, 0X8)
    data_file_id = ctype.BField(ctype.c_uint32, 3, 0X8)
    block_offset = ctype.BField(ctype.c_uint32, 28, 0X8)
    synonym_index = ctype.SField(ctype.c_uint32, 0XC)
    path = ctype.SField(ctype.c_char[240], 0X10)


class HashTableElem_Hash32(ctype.Struct):
    _size_ = 0X8

    hash_hoge = ctype.SField(ctype.c_uint32, 0X0)
    is_synonym = ctype.BField(ctype.c_uint32, 1, 0X4)
    data_file_id = ctype.BField(ctype.c_uint32, 3, 0X4)
    block_offset = ctype.BField(ctype.c_uint32, 28, 0X4)


class HashTableElem_Hash64(ctype.Struct):
    _size_ = 0X10

    hash_hoge = ctype.SField(ctype.c_uint64, 0X0)
    is_synonym = ctype.BField(ctype.c_uint32, 1, 0X8)
    data_file_id = ctype.BField(ctype.c_uint32, 3, 0X8)
    block_offset = ctype.BField(ctype.c_uint32, 28, 0X8)
