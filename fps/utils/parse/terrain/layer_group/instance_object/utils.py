import ctypes
import enum
import functools
import typing

from glm import vec3, make_vec3

from nylib import ctype
from ..utils import AssetType
from ...utils import offset_string, Color, ColorHDRI

float_p = ctypes.POINTER(ctypes.c_float)


class TriggerBoxShape(enum.IntEnum):
    Box = 0X1
    Sphere = 0X2
    Cylinder = 0X3
    Board = 0X4
    Mesh = 0X5
    BoardBothSides = 0X6


class Transformation(typing.NamedTuple):
    translation: vec3
    rotation: vec3
    scale: vec3

    @classmethod
    def from_ctypes(cls, src: 'ctype.c_float * 3 * 3') -> 'Transformation':
        return cls(
            # make_vec3(src[0]._address_),
            # make_vec3(src[1]._address_),
            # make_vec3(src[2]._address_),
            *(make_vec3(ctypes.cast(el._address_, float_p)) for el in src),
        )


class RelativePositions(ctype.Struct):
    _size_ = 0X8
    _pos = ctype.SField(ctype.c_int32, 0X0)
    pos_count = ctype.SField(ctype.c_int32, 0X4)

    @functools.cached_property
    def pos(self):
        return (ctype.c_uint8 * self.pos_count)(_address_=self._address_ + self._pos)


class InstanceObject(ctype.Struct):
    asset_type = ctype.SField(ctype.c_int32, 0X0)
    instance_id = ctype.SField(ctype.c_uint32, 0X4)
    _name = ctype.SField(ctype.c_int32, 0X8)
    _transformation = ctype.Field(ctype.c_float * 3 * 3, 0XC)

    @property
    def e_asset_type(self):
        return AssetType(self.asset_type)

    name = offset_string('_name')

    @functools.cached_property
    def transformation(self):
        return Transformation.from_ctypes(self._transformation)

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.instance_id}, asset_type={self.e_asset_type.name}, name={self.name})'
