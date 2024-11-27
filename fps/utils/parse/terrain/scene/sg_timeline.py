import ctypes
import enum
import functools

from nylib import ctype
from ..utils import offset_string


class CollisionState(enum.IntEnum):
    NoChange = 0X0
    On = 0X1
    Off = 0X2


class SGActorBinder(ctype.Struct):
    _size_ = 0X8
    actor_type = ctype.SField(ctype.c_uint32, 0X0)
    instance_id = ctype.SField(ctype.c_uint32, 0X4)


class SGTimeline(ctype.Struct):
    _size_ = 0X2C

    member_id = ctype.SField(ctype.c_uint32, 0X0)
    _name = ctype.SField(ctype.c_int32, 0X4)
    _binders = ctype.SField(ctype.c_int32, 0X8)
    binder_count = ctype.SField(ctype.c_int32, 0XC)
    _binary_asset_path = ctype.SField(ctype.c_int32, 0X10)
    _binary = ctype.SField(ctype.c_int32, 0X14)
    binary_count = ctype.SField(ctype.c_int32, 0X18)
    timeline_id = ctype.SField(ctype.c_uint32, 0X1C)
    auto_play = ctype.SField(ctype.c_int8, 0X20)
    loop_playback = ctype.SField(ctype.c_int8, 0X21)
    collision_state = ctype.SField(ctype.c_uint32, 0X24)

    name = offset_string('_name')
    binary_asset_path = offset_string('_binary_asset_path')

    @property
    def e_collision_state(self):
        return CollisionState(self.collision_state)

    @functools.cached_property
    def binders(self):
        return (SGActorBinder * self.binder_count)(_address_=self._address_ + self._binders)

    @functools.cached_property
    def binary(self):
        return (ctype.c_uint8 * self.binary_count)(_address_=self._address_ + self._binary)


class SGTimelineFolder(ctype.Struct):
    _size_ = 0X8

    _sg_timelines = ctype.SField(ctype.c_int32, 0X0)
    sg_timeline_count = ctype.SField(ctype.c_int32, 0X4)

    @property
    def sg_timelines(self):
        return (SGTimeline * self.sg_timeline_count)(_address_=self._address_ + self._sg_timelines)
