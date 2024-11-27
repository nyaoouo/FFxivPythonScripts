import enum
import functools
import struct

from nylib import ctype
from ..utils import offset_string, Color, ColorHDRI


class SGActionType(enum.IntEnum):
    Null = 0X0
    Door = 0X1
    Rotation = 0X2
    RandomTimeline = 0X3
    Clock = 0X4
    Transform = 0X5
    Color = 0X6


class SGAction(ctype.Struct):
    sg_action_type = ctype.SField(ctype.c_int32, 0X0)
    enabled = ctype.SField(ctype.c_int8, 0X4)

    @property
    def e_sg_action_type(self):
        return SGActionType(self.sg_action_type)


class SGActionClock(SGAction):
    hour_hand_instance_id = ctype.SField(ctype.c_uint8, 0X10)
    minute_hand_instance_id = ctype.SField(ctype.c_uint8, 0X11)


class SGActionColor(SGAction):
    class Item(SGAction):
        class CurveType(enum.IntEnum):
            Linear = 0X0
            Spline = 0X1

        class BlinkType(enum.IntEnum):
            SineCurve = 0X0
            Random = 0X1

        enabled = ctype.SField(ctype.c_int8, 0X0)
        color_enabled = ctype.SField(ctype.c_int8, 0X1)
        color_start: 'ColorHDRI' = eval('0X4')
        color_end: 'ColorHDRI' = eval('0XC')
        power_enabled = ctype.SField(ctype.c_int8, 0X14)
        power_start = ctype.SField(ctype.c_float, 0X18)
        power_end = ctype.SField(ctype.c_float, 0X1C)
        time = ctype.SField(ctype.c_uint32, 0X20)
        curve = ctype.SField(ctype.c_int32, 0X24)
        blink_enabled = ctype.SField(ctype.c_int8, 0X28)
        blink_amplitude = ctype.SField(ctype.c_float, 0X2C)
        blink_speed = ctype.SField(ctype.c_float, 0X30)
        blink_type = ctype.SField(ctype.c_int32, 0X34)
        blink_sync = ctype.SField(ctype.c_int8, 0X38)

        @property
        def e_curve(self):
            return self.CurveType(self.curve)

        @property
        def e_blink_type(self):
            return self.BlinkType(self.blink_type)

    _target_sg_member_ids = ctype.SField(ctype.c_int32, 0X10)
    target_sg_member_id_count = ctype.SField(ctype.c_int32, 0X14)
    loop = ctype.SField(ctype.c_int8, 0X18)
    _emissive = ctype.SField(ctype.c_int32, 0X20)
    _light = ctype.SField(ctype.c_int32, 0X24)

    @functools.cached_property
    def target_sg_member_ids(self):
        return (ctype.c_uint8 * self.target_sg_member_id_count)(_address_=self._address_ + self._target_sg_member_ids)

    @functools.cached_property
    def emissive(self):
        return self.Item(_address_=self._address_ + self._emissive)

    @functools.cached_property
    def light(self):
        return self.Item(_address_=self._address_ + self._light)


class SGActionRandomTimeline(SGAction):
    class Item(ctype.Struct):
        _size_ = 0X2
        timeline_id = ctype.SField(ctype.c_uint8, 0X0)
        probability = ctype.SField(ctype.c_uint8, 0X1)

    _random_timeline_items = ctype.SField(ctype.c_int32, 0X10)
    random_timeline_item_count = ctype.SField(ctype.c_int32, 0X14)

    @functools.cached_property
    def random_timeline_items(self):
        return (self.Item * self.random_timeline_item_count)(_address_=self._address_ + self._random_timeline_items)


class SGActionRotation(SGAction):
    class RotationAxis(enum.IntEnum):
        X = 0X0
        Y = 0X1
        Z = 0X2

    bg_instance_id = ctype.SField(ctype.c_uint8, 0X10)
    rotation_axis = ctype.SField(ctype.c_int32, 0X14)
    round_time = ctype.SField(ctype.c_float, 0X18)
    start_end_time = ctype.SField(ctype.c_float, 0X1C)
    vfx_instance_id = ctype.SField(ctype.c_uint8, 0X20)
    vfx_rotation_with_bg = ctype.SField(ctype.c_int8, 0X21)
    sound_at_starting = ctype.SField(ctype.c_uint8, 0X22)
    sound_at_rounding = ctype.SField(ctype.c_uint8, 0X23)
    sound_at_stopping = ctype.SField(ctype.c_uint8, 0X24)
    vfx_instance_id2 = ctype.SField(ctype.c_uint8, 0X25)
    vfx_rotation_with_bg2 = ctype.SField(ctype.c_int8, 0X26)

    @property
    def e_rotation_axis(self):
        return self.RotationAxis(self.rotation_axis)


class SGActionTransform(SGAction):
    class Item(ctype.Struct):
        class CurveType(enum.IntEnum):
            CurveLinear = 0X0
            CurveSpline = 0X1
            CurveAcceleration = 0X2
            CurveDeceleration = 0X3

        class MovementType(enum.IntEnum):
            MovementOneWay = 0X0
            MovementRoundTrip = 0X1
            MovementRepetition = 0X2

        _size_ = 0X24

        enabled = ctype.SField(ctype.c_int8, 0X0)
        offset = ctype.Field(ctype.c_float * 3, 0X4)
        random_rate = ctype.SField(ctype.c_float, 0X10)
        time = ctype.SField(ctype.c_uint32, 0X14)
        start_end_time = ctype.SField(ctype.c_uint32, 0X18)
        curve_type = ctype.SField(ctype.c_int32, 0X1C)
        movement_type = ctype.SField(ctype.c_int32, 0X20)

        @property
        def e_curve_type(self):
            return self.CurveType(self.curve_type)

        @property
        def e_movement_type(self):
            return self.MovementType(self.movement_type)

    _size_ = 0X2C

    _target_sg_member_ids = ctype.SField(ctype.c_int32, 0X10)
    target_sg_member_id_count = ctype.SField(ctype.c_int32, 0X14)
    loop = ctype.SField(ctype.c_int8, 0X18)
    _translation = ctype.SField(ctype.c_int32, 0X20)
    _rotation = ctype.SField(ctype.c_int32, 0X24)
    _scale = ctype.SField(ctype.c_int32, 0X28)

    @functools.cached_property
    def target_sg_member_ids(self):
        return (ctype.c_uint8 * self.target_sg_member_id_count)(_address_=self._address_ + self._target_sg_member_ids)

    @functools.cached_property
    def translation(self):
        return self.Item(_address_=self._address_ + self._translation)

    @functools.cached_property
    def rotation(self):
        return self.Item(_address_=self._address_ + self._rotation)

    @functools.cached_property
    def scale(self):
        return self.Item(_address_=self._address_ + self._scale)


class SGActionDoor(SGAction):
    class CurveType(enum.IntEnum):
        Spline = 0X1
        Linear = 0X2
        Acceleration = 0X3
        Deceleration = 0X4

    class DoorRotationAxis(enum.IntEnum):
        X = 0X0
        Y = 0X1
        Z = 0X2

    class OpenStyle(enum.IntEnum):
        Rotation = 0X0
        HorizontalSlide = 0X1
        VerticalSlide = 0X2

    # Common::DevEnv::Generated::SGActionDoor_t
    _size_ = 0X30

    door_instance_id1 = ctype.SField(ctype.c_uint8, 0X10)
    door_instance_id2 = ctype.SField(ctype.c_uint8, 0X11)
    open_style = ctype.SField(ctype.c_int32, 0X14)
    time_length = ctype.SField(ctype.c_float, 0X18)
    open_angle = ctype.SField(ctype.c_float, 0X1C)
    open_distance = ctype.SField(ctype.c_float, 0X20)
    sound_at_opening = ctype.SField(ctype.c_uint8, 0X24)
    sound_at_closing = ctype.SField(ctype.c_uint8, 0X25)
    door_instance_id3 = ctype.SField(ctype.c_uint8, 0X26)
    door_instance_id4 = ctype.SField(ctype.c_uint8, 0X27)
    curve_type = ctype.SField(ctype.c_int32, 0X28)
    rotation_axis = ctype.SField(ctype.c_int32, 0X2C)

    @property
    def e_open_style(self):
        return self.OpenStyle(self.open_style)

    @property
    def e_curve_type(self):
        return self.CurveType(self.curve_type)

    @property
    def e_rotation_axis(self):
        return self.DoorRotationAxis(self.rotation_axis)


sg_action_map = {
    SGActionType.Door: SGActionDoor,
    SGActionType.Rotation: SGActionRotation,
    SGActionType.RandomTimeline: SGActionRandomTimeline,
    SGActionType.Clock: SGActionClock,
    SGActionType.Transform: SGActionTransform,
    SGActionType.Color: SGActionColor,
}


def get_sg_action(buf, off=0) -> SGAction:
    return ctype.cdata_from_buffer(buf, sg_action_map.get(struct.unpack_from(b'I', buf, off)[0]) or SGAction, off)


def get_sg_action_from_addr(addr) -> SGAction:
    return (sg_action_map.get(ctype.c_int32(_address_=addr).value) or SGAction)(_address_=addr)
