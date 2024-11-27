import enum
import struct

from .utils import *


class SGOverriddenMember(ctype.Struct):
    asset_type = ctype.SField(ctype.c_int32, 0X0)
    member_id = ctype.Field(ctype.c_uint8 * 4, 0X4)


class SGOverriddenVFX(SGOverriddenMember):
    color_enable = ctype.SField(ctype.c_int8, 0X8)
    color: 'Color' = eval('0X9')
    is_auto_play = ctype.SField(ctype.c_uint8, 0XD)
    z_correct_enable = ctype.SField(ctype.c_int8, 0XE)
    z_correct = ctype.SField(ctype.c_float, 0X10)


class SGOverriddenLight(SGOverriddenMember):
    diffuse_color_hdri: 'ColorHDRI' = eval('0X8')
    shadow_clip_range = ctype.SField(ctype.c_float, 0X10)
    specular_enabled = ctype.SField(ctype.c_int8, 0X14)
    bg_shadow_enabled = ctype.SField(ctype.c_int8, 0X15)
    character_shadow_enabled = ctype.SField(ctype.c_int8, 0X16)
    merge_group_id = ctype.SField(ctype.c_uint16, 0X18)
    diffuse_color_hdr_edited = ctype.SField(ctype.c_int8, 0X1A)
    shadow_clip_range_edited = ctype.SField(ctype.c_int8, 0X1B)
    specular_enabled_edited = ctype.SField(ctype.c_int8, 0X1C)
    bg_shadow_enabled_edited = ctype.SField(ctype.c_int8, 0X1D)
    character_shadow_enabled_edited = ctype.SField(ctype.c_int8, 0X1E)
    merge_group_id_edited = ctype.SField(ctype.c_int8, 0X1F)


class SGOverriddenBG(SGOverriddenMember):
    render_shadow_enabled = ctype.SField(ctype.c_uint8, 0X8)
    render_light_shadow_enabled = ctype.SField(ctype.c_uint8, 0X9)
    render_model_clip_range = ctype.SField(ctype.c_float, 0XC)
    is_visible = ctype.SField(ctype.c_uint8, 0X10)
    collision_exist = ctype.SField(ctype.c_uint8, 0X11)
    nav_mesh_disable = ctype.SField(ctype.c_uint8, 0X12)


class SGOverriddenSE(SGOverriddenMember):
    auto_play = ctype.SField(ctype.c_uint8, 0X8)


def sg_member_type(asset_type):
    if asset_type == AssetType.BG.value:
        return SGOverriddenBG  # .from_buffer(source, offset)
    if asset_type == AssetType.VFX.value:
        return SGOverriddenVFX  # .from_buffer(source, offset)
    if asset_type == AssetType.LayLight.value:
        return SGOverriddenLight  # .from_buffer(source, offset)
    if asset_type == AssetType.Sound.value:
        return SGOverriddenSE  # .from_buffer(source, offset)
    return SGOverriddenMember  # .from_buffer(source, offset)


class MovePathSettings(ctype.Struct):
    class Mode(enum.IntEnum):
        Null = 0X0
        SGAction = 0X1
        Timeline = 0X2

    class RotationType(enum.IntEnum):
        NoRotate = 0X0
        AllAxis = 0X1
        YAxisOnly = 0X2

    mode = ctype.SField(ctype.c_int32, 0X0)
    auto_play = ctype.SField(ctype.c_int8, 0X4)
    time = ctype.SField(ctype.c_uint16, 0X6)
    loop = ctype.SField(ctype.c_int8, 0X8)
    reverse = ctype.SField(ctype.c_int8, 0X9)
    rotation = ctype.SField(ctype.c_int32, 0XC)
    accelerate_time = ctype.SField(ctype.c_uint16, 0X10)
    decelerate_time = ctype.SField(ctype.c_uint16, 0X12)
    vertical_swing_range = ctype.Field(ctype.c_float * 2, 0X14)
    horizontal_swing_range = ctype.Field(ctype.c_float * 2, 0X1C)
    swing_move_speed_range = ctype.Field(ctype.c_float * 2, 0X24)
    swing_rotation = ctype.Field(ctype.c_float * 2, 0X2C)
    swing_rotation_speed_range = ctype.Field(ctype.c_float * 2, 0X34)

    @property
    def e_mode(self):
        return self.Mode(self.mode)

    @property
    def e_rotation(self):
        return self.RotationType(self.rotation)


class SGInstanceObject(InstanceObject):
    class ColorState(enum.IntEnum):
        Play = 0X0
        Stop = 0X1
        Replay = 0X2
        Reset = 0X3

    class TransformState(enum.IntEnum):
        Play = 0X0
        Stop = 0X1
        Replay = 0X2
        Reset = 0X3

    class RotationState(enum.IntEnum):
        Rounding = 0X1
        Stopped = 0X2

    class DoorState(enum.IntEnum):
        Auto = 0X1
        Open = 0X2
        Closed = 0X3

    _asset_path = ctype.SField(ctype.c_int32, 0X30)
    initial_door_state = ctype.SField(ctype.c_int32, 0X34)
    _overridden_members = ctype.SField(ctype.c_int32, 0X38)
    overridden_member_count = ctype.SField(ctype.c_int32, 0X3C)
    initial_rotation_state = ctype.SField(ctype.c_int32, 0X40)
    random_timeline_auto_play = ctype.SField(ctype.c_int8, 0X44)
    random_timeline_loop_playback = ctype.SField(ctype.c_int8, 0X45)
    is_collision_controllable_without_e_obj = ctype.SField(ctype.c_int8, 0X46)
    disable_error_check = ctype.SField(ctype.c_int8, 0X47)
    bound_client_path_instance_id = ctype.SField(ctype.c_uint32, 0X48)
    _move_path_settings = ctype.SField(ctype.c_int32, 0X4C)
    not_create_nav_mesh_door = ctype.SField(ctype.c_int8, 0X50)
    initial_transform_state = ctype.SField(ctype.c_int32, 0X54)
    initial_color_state = ctype.SField(ctype.c_int32, 0X58)

    @property
    def e_initial_door_state(self):
        return self.DoorState(self.initial_door_state)

    @property
    def e_initial_rotation_state(self):
        return self.RotationState(self.initial_rotation_state)

    @property
    def e_initial_transform_state(self):
        return self.TransformState(self.initial_transform_state)

    @property
    def e_initial_color_state(self):
        return self.ColorState(self.initial_color_state)

    asset_path = offset_string('_asset_path')

    @functools.cached_property
    def overridden_members(self) -> list[SGOverriddenMember]:
        p_offset = self._address_ + self._overridden_members
        return [
            sg_member_type(ctype.c_int32(_address_=(a := p_offset + o.value)).value)(_address_=a)
            for o in (ctype.c_int32 * self.overridden_member_count)(_address_=p_offset)
        ]

    @property
    def move_path_settings(self):
        return MovePathSettings(_address_=self._address_ + self._move_path_settings)
