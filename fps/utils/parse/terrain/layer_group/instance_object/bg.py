import ctypes
import enum
from .utils import *


class ModelCollisionType(enum.IntEnum):
    Null = 0X0
    Replace = 0X1
    TYPE_Box = 0X2


class ModelCollisionConfig(ctype.Struct):

    collision_attribute_mask = ctype.SField(ctype.c_uint32, 0X0)
    collision_attribute = ctype.SField(ctype.c_uint32, 0X4)
    collision_attribute2_mask = ctype.SField(ctype.c_uint32, 0X8)
    collision_attribute2 = ctype.SField(ctype.c_uint32, 0XC)
    collision_box_shape = ctype.SField(ctype.c_uint32, 0X10)
    _collision_box_transformation = ctype.Field(ctype.c_float * 3 * 3, 0X14)
    aabb_min_x = ctype.SField(ctype.c_float, 0X38)
    aabb_min_y = ctype.SField(ctype.c_float, 0X3C)
    aabb_min_z = ctype.SField(ctype.c_float, 0X40)
    aabb_max_x = ctype.SField(ctype.c_float, 0X44)
    aabb_max_y = ctype.SField(ctype.c_float, 0X48)
    aabb_max_z = ctype.SField(ctype.c_float, 0X4C)

    @property
    def e_collision_box_shape(self):
        return TriggerBoxShape(self.collision_box_shape)

    @functools.cached_property
    def collision_box_transformation(self):
        return Transformation.from_ctypes(self._collision_box_transformation)


class BGInstanceObject(InstanceObject):
    _asset_path = ctype.SField(ctype.c_int32, 0X30)
    _collision_asset_path = ctype.SField(ctype.c_int32, 0X34)
    collision_type = ctype.SField(ctype.c_int32, 0X38)
    attribute_mask = ctype.SField(ctype.c_uint32, 0X3C)
    attribute = ctype.SField(ctype.c_uint32, 0X40)
    attribute2_mask = ctype.SField(ctype.c_uint32, 0X44)
    attribute2 = ctype.SField(ctype.c_uint32, 0X48)
    _collision_config = ctype.SField(ctype.c_int32, 0X4C)
    is_visible = ctype.SField(ctype.c_int8, 0X50)
    render_shadow_enabled = ctype.SField(ctype.c_uint8, 0X51)
    render_light_shadow_enabled = ctype.SField(ctype.c_uint8, 0X52)
    render_model_clip_range = ctype.SField(ctype.c_float, 0X54)
    bounding_sphere_radius = ctype.SField(ctype.c_float, 0X58)

    collision_asset_path = offset_string('_collision_asset_path')
    asset_path = offset_string('_asset_path')

    @property
    def e_collision_type(self):
        return ModelCollisionType(self.collision_type)

    @property
    def collision_config(self):
        return ModelCollisionConfig(_address_=self._address_ + self._collision_config)
