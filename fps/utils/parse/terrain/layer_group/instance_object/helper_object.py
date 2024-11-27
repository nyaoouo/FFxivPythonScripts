import enum

from .utils import *


class TargetType(enum.IntEnum):
    Null = 0X0
    ENPCInstanceID = 0X1
    Player = 0X2
    PartyMember = 0X3
    ENPCDirect = 0X4
    BNPCDirect = 0X5
    BGObjInstanceID = 0X6
    SharedGroupInstanceID = 0X7
    BGObj = 0X8
    SharedGroup = 0X9
    Weapon = 0XA
    StableChocobo = 0XB
    AllianceMember = 0XC
    GuestMember = 0XD
    GroomPlayer = 0XE
    BridePlayer = 0XF
    CustomSharedGroup = 0X10


class WeaponModel(ctype.Struct):
    skeleton_id = ctype.SField(ctype.c_uint16, 0X0)
    pattern_id = ctype.SField(ctype.c_uint16, 0X2)
    image_change_id = ctype.SField(ctype.c_uint16, 0X4)
    staining_id = ctype.SField(ctype.c_uint16, 0X6)


class HelperObjInstanceObject(InstanceObject):
    obj_type = ctype.SField(ctype.c_uint32, 0X30)
    target_type = ctype.SField(ctype.c_uint32, 0X34)  # TargetType
    specific = ctype.SField(ctype.c_int8, 0X38)
    character_size = ctype.SField(ctype.c_uint8, 0X39)
    use_default_motion = ctype.SField(ctype.c_int8, 0X3A)
    party_member_index = ctype.SField(ctype.c_uint8, 0X3B)
    target_instance_id = ctype.SField(ctype.c_uint32, 0X3C)
    direct_id = ctype.SField(ctype.c_uint32, 0X40)
    use_direct_id = ctype.SField(ctype.c_int8, 0X44)
    keep_high_texture = ctype.SField(ctype.c_int8, 0X45)
    weapon: 'WeaponModel' = eval('0X46')
    alliance_member_index = ctype.SField(ctype.c_uint8, 0X4E)
    guest_member_index = ctype.SField(ctype.c_uint8, 0X4F)
    sky_visibility = ctype.SField(ctype.c_float, 0X50)
    other_instance_object = ctype.SField(ctype.c_int32, 0X54)
    use_transform = ctype.SField(ctype.c_int8, 0X58)
    model_lod = ctype.SField(ctype.c_uint8, 0X59)
    texture_lod = ctype.SField(ctype.c_uint8, 0X5A)
    draw_head_parts = ctype.SField(ctype.c_uint8, 0X5B)
    _default_transform = ctype.Field(ctype.c_float * 3 * 3, 0X5C)
    dummy = ctype.SField(ctype.c_int8, 0X80)
    disable_hide_weapon_config = ctype.SField(ctype.c_int8, 0X81)
    replace_player_customize = ctype.SField(ctype.c_int8, 0X82)
    extend_parameter = ctype.SField(ctype.c_int32, 0X88)

    @functools.cached_property
    def default_transform(self):
        return Transformation.from_ctypes(self._default_transform)

    @property
    def e_target_type(self):
        return TargetType(self.target_type)
