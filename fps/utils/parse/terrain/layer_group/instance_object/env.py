import enum

from .utils import *


class EnvLocationInstanceObject(InstanceObject):
    _sh_ambient_light_asset_path = ctype.SField(ctype.c_int32, 0X30)
    _env_map_asset_path = ctype.SField(ctype.c_int32, 0X34)
    sh_ambient_light_asset_path = offset_string('_sh_ambient_light_asset_path')
    env_map_asset_path = offset_string('_env_map_asset_path')


class EnvSetInstanceObject(InstanceObject):
    class Shape(enum.IntEnum):
        Ellipsoid = 0X1
        Cuboid = 0X2
        Cylinder = 0X3

    _asset_path = ctype.SField(ctype.c_int32, 0X30)
    bound_instance_id = ctype.SField(ctype.c_uint32, 0X34)
    shape = ctype.SField(ctype.c_int32, 0X38)
    is_env_map_shooting_point = ctype.SField(ctype.c_int8, 0X3C)
    priority = ctype.SField(ctype.c_uint8, 0X3D)
    effective_range = ctype.SField(ctype.c_float, 0X40)
    interpolation_time = ctype.SField(ctype.c_int32, 0X44)
    reverb = ctype.SField(ctype.c_float, 0X48)
    filter = ctype.SField(ctype.c_float, 0X4C)
    _sound_asset_path = ctype.SField(ctype.c_int32, 0X50)

    asset_path = offset_string('_asset_path')
    sound_asset_path = offset_string('_sound_asset_path')

    @property
    def e_shape(self):
        return self.Shape(self.shape)
