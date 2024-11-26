import enum

from nylib import ctype

from ..utils import FileCommonHeader


class Attribute(enum.IntFlag):
    DISCARD_PER_FRAME = 1 << 0
    DISCARD_PER_MAP = 1 << 1
    MANAGED = 1 << 2
    USER_MANAGED = 1 << 3
    CPU_READ = 1 << 4
    LOCATION_MAIN = 1 << 5
    NO_GPU_READ = 1 << 6
    ALIGNED_SIZE = 1 << 7
    EDGE_CULLING = 1 << 8
    LOCATION_ONION = 1 << 9
    READ_WRITE = 1 << 10
    IMMUTABLE = 1 << 11
    IMMUTABLE_CPU_READ = 1 << 12
    DYNAMIC_NO_DISCARD = 1 << 13
    DISCARD_DIRECT_CONSTANT = 1 << 14
    CPU_READ_WRITE = 1 << 15
    INDIRECT_ARGS = 1 << 16

    TEXTURE_RENDER_TARGET = 1 << 20
    TEXTURE_DEPTH_STENCIL = 1 << 21
    TEXTURE_TYPE_1D = 1 << 22
    TEXTURE_TYPE_2D = 1 << 23
    TEXTURE_TYPE_3D = 1 << 24
    TEXTURE_TYPE_CUBE = 1 << 25
    TEXTURE_SWIZZLE = 1 << 26
    TEXTURE_NO_TILED = 1 << 27
    TEXTURE_TYPE_2D_ARRAY = 1 << 28
    TEXTURE_NO_SWIZZLE = 1 << 31


FMT_INTEGER = 0X1
FMT_FLOAT = 0X2
FMT_DXT = 0X3
FMT_DEPTH_STENCIL = 0X4
FMT_SPECIAL = 0X5
FMT_BC = 0X6
FMT_FLOAT_UNorm = 0X7


def _tf(t, a1, a2, a3):
    return (t << 12) | (a1 << 8) | (a2 << 4) | a3


class TextureFormat(enum.IntEnum):
    NULL = _tf(FMT_SPECIAL, 1, 0, 0)

    R8G8B8A8_UNorm = _tf(FMT_INTEGER, 4, 5, 0)
    R8G8B8X8_UNorm = _tf(FMT_INTEGER, 4, 5, 1)
    R4G4B4A4_UNorm = _tf(FMT_INTEGER, 4, 4, 0)
    R5G5B5A1_UNorm = _tf(FMT_INTEGER, 4, 4, 1)

    L8_UNorm = _tf(FMT_INTEGER, 1, 3, 0)
    A8_UNorm = _tf(FMT_INTEGER, 1, 3, 1)
    R8_UNorm = _tf(FMT_INTEGER, 1, 3, 2)
    R8_INT = _tf(FMT_INTEGER, 1, 3, 3)

    R16_INT = _tf(FMT_INTEGER, 1, 4, 0)
    R16_FLOAT = _tf(FMT_FLOAT, 1, 4, 0)
    R16_UNorm = _tf(FMT_FLOAT_UNorm, 1, 4, 0)

    R32_INT = _tf(FMT_INTEGER, 1, 5, 0)
    R32_FLOAT = _tf(FMT_FLOAT, 1, 5, 0)
    R32G32_FLOAT = _tf(FMT_FLOAT, 2, 6, 0)
    R32G32B32A32_FLOAT = _tf(FMT_FLOAT, 4, 7, 0)

    R8G8_UNorm = _tf(FMT_INTEGER, 2, 4, 0)

    R16G16_FLOAT = _tf(FMT_FLOAT, 2, 5, 0)
    R16G16_UNorm = _tf(FMT_FLOAT_UNorm, 2, 5, 0)
    R16G16B16A16_FLOAT = _tf(FMT_FLOAT, 4, 6, 0)

    DXT1 = _tf(FMT_DXT, 4, 2, 0)
    DXT3 = _tf(FMT_DXT, 4, 3, 0)
    DXT5 = _tf(FMT_DXT, 4, 3, 1)

    BC5 = _tf(FMT_BC, 2, 3, 0)
    BC7 = _tf(FMT_BC, 4, 3, 2)

    D16 = _tf(FMT_DEPTH_STENCIL, 1, 4, 0)
    D24S8 = _tf(FMT_DEPTH_STENCIL, 2, 5, 0)
    SHADOW16 = _tf(FMT_SPECIAL, 1, 4, 0)
    SHADOW24 = _tf(FMT_SPECIAL, 1, 5, 0)


class FileTexture(FileCommonHeader):
    _size_ = 0X18

    output_lod_num = ctype.SField(ctype.c_uint32, 0X14)


class TextureHeader(ctype.Struct):
    _size_ = 0x50

    type_ = ctype.SField(ctype.c_uint32, 0x0)
    format_ = ctype.SField(ctype.c_uint32, 0x4)
    width = ctype.SField(ctype.c_uint16, 0x8)
    height = ctype.SField(ctype.c_uint16, 0xa)
    depth = ctype.SField(ctype.c_uint16, 0xc)
    mip_levels = ctype.SField(ctype.c_uint8, 0xe)
    array_size = ctype.SField(ctype.c_uint8, 0xf)
    lod_offset = ctype.Field(ctype.c_uint32 * 3, 0x10)
    offset_to_surface = ctype.Field(ctype.c_uint32 * 13, 0x1c)

    @property
    def type(self):
        return Attribute(self.type_)

    @type.setter
    def type(self, value):
        self.type_ = value

    @property
    def format(self):
        return TextureFormat(self.format_)

    @format.setter
    def format(self, value):
        self.format_ = value


class LodBlock(ctype.Struct):
    _size_ = 0x14

    comp_offset = ctype.SField(ctype.c_uint32, 0x0)
    comp_size = ctype.SField(ctype.c_uint32, 0x4)
    decomp_size = ctype.SField(ctype.c_uint32, 0x8)
    block_offset = ctype.SField(ctype.c_uint32, 0xc)
    block_num = ctype.SField(ctype.c_uint32, 0x10)
