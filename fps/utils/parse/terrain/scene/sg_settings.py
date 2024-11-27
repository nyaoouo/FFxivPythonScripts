import ctypes
import enum
import functools

from nylib import ctype
from .sg_action import get_sg_action_from_addr


class ShowHideAnimationType(enum.IntEnum):
    Invalid = 0X0
    Null = 0X1
    Auto = 0X2
    Timeline = 0X3
    AutoWithAnimationTime = 0X4


class SGActionFolder(ctype.Struct):
    _size_ = 0X8

    _sg_actions = ctype.SField(ctype.c_int32, 0X0)
    sg_action_count = ctype.SField(ctype.c_int32, 0X4)

    @property
    def sg_actions(self):
        p_offset = self._address_ + self._sg_actions
        return [get_sg_action_from_addr(p_offset + o.value) for o in (ctype.c_int32 * self.sg_action_count)(_address_=p_offset)]


class SGSettings(ctype.Struct):
    _size_ = 0X24

    name_plate_instance_id = ctype.SField(ctype.c_uint8, 0X0)
    timeline_showing_id = ctype.SField(ctype.c_uint8, 0X1)
    timeline_hiding_id = ctype.SField(ctype.c_uint8, 0X2)
    timeline_shown_id = ctype.SField(ctype.c_uint8, 0X3)
    timeline_hidden_id = ctype.SField(ctype.c_uint8, 0X4)
    general_purpose_timeline_ids = ctype.Field(ctype.c_uint8 * 16, 0X5)
    timeline_showing_id_enabled = ctype.SField(ctype.c_int8, 0X15)
    timeline_hiding_id_enabled = ctype.SField(ctype.c_int8, 0X16)
    need_system_actor = ctype.SField(ctype.c_int8, 0X17)
    show_hide_animation_type = ctype.SField(ctype.c_int32, 0X18)
    show_animation_time = ctype.SField(ctype.c_uint16, 0X1C)
    hide_animation_time = ctype.SField(ctype.c_uint16, 0X1E)
    _sg_action_folder = ctype.SField(ctype.c_int32, 0X20)

    @property
    def e_show_hide_animation_type(self):
        return ShowHideAnimationType(self.show_hide_animation_type)

    @functools.cached_property
    def sg_actions(self):
        return SGActionFolder(_address_=self._address_ + self._sg_action_folder).sg_actions
