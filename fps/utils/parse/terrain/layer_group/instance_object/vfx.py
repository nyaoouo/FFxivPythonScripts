from .utils import *


class VFXInstanceObject(InstanceObject):
    _asset_path = ctype.SField(ctype.c_int32, 0X30)
    soft_particle_fade_range = ctype.SField(ctype.c_float, 0X34)
    color: 'Color' = eval('0X3C')
    is_auto_play = ctype.SField(ctype.c_int8, 0X40)
    is_no_far_clip = ctype.SField(ctype.c_int8, 0X41)
    fade_near_start = ctype.SField(ctype.c_float, 0X44)
    fade_near_end = ctype.SField(ctype.c_float, 0X48)
    fade_far_start = ctype.SField(ctype.c_float, 0X4C)
    fade_far_end = ctype.SField(ctype.c_float, 0X50)
    z_correct = ctype.SField(ctype.c_float, 0X54)
    asset_path = offset_string('_asset_path')
