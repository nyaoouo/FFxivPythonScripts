import enum

from .utils import *


class TriggerBoxInstanceObject(InstanceObject):

    trigger_box_shape = ctype.SField(ctype.c_uint32, 0X30)
    priority = ctype.SField(ctype.c_int16, 0X34)
    enabled = ctype.SField(ctype.c_int8, 0X36)

    @property
    def e_trigger_box_shape(self):
        return TriggerBoxShape(self.trigger_box_shape)


class EventEffectRangeInstanceObject(TriggerBoxInstanceObject):
    pass


class EventRangeInstanceObject(TriggerBoxInstanceObject):
    is_checked_on_server = ctype.SField(ctype.c_int8, 0X3C)
    is_bnpc_target = ctype.SField(ctype.c_int8, 0X3D)
    is_line_check = ctype.SField(ctype.c_int8, 0X3E)
    is_pc_target = ctype.SField(ctype.c_int8, 0X3F)
    is_pet_target = ctype.SField(ctype.c_int8, 0X40)
    is_not_out_death = ctype.SField(ctype.c_int8, 0X41)
    is_akatsuki_target = ctype.SField(ctype.c_int8, 0X42)


class ClickableRangeInstanceObject(TriggerBoxInstanceObject):
    pass


class GimmickRangeInstanceObject(TriggerBoxInstanceObject):
    class GimmickType(enum.IntEnum):
        Fishing = 0X1
        Content = 0X2
        Room = 0X3

    gimmick_type = ctype.SField(ctype.c_uint32, 0X3C)
    gimmick_key = ctype.SField(ctype.c_uint32, 0X40)
    room_use_attribute = ctype.SField(ctype.c_int8, 0X44)
    group_id = ctype.SField(ctype.c_uint8, 0X45)
    enabled_in_dead = ctype.SField(ctype.c_int8, 0X46)

    @property
    def e_gimmick_type(self):
        return self.GimmickType(self.gimmick_type)


class CollisionBoxInstanceObject(TriggerBoxInstanceObject):
    attribute_mask = ctype.SField(ctype.c_uint32, 0X3C)
    attribute = ctype.SField(ctype.c_uint32, 0X40)
    attribute2_mask = ctype.SField(ctype.c_uint32, 0X44)
    attribute2 = ctype.SField(ctype.c_uint32, 0X48)
    push_player_out = ctype.SField(ctype.c_int8, 0X4C)
    _collision_asset_path = ctype.SField(ctype.c_int32, 0X50)
    collision_asset_path = offset_string('_collision_asset_path')


class WaterRangeInstanceObject(TriggerBoxInstanceObject):
    underwater_enabled = ctype.SField(ctype.c_int8, 0X3C)
    disable_flapping = ctype.SField(ctype.c_int8, 0X3D)


class SphereCastRangeInstanceObject(TriggerBoxInstanceObject):
    pass


class ShowHideRangeInstanceObject(TriggerBoxInstanceObject):
    _layer_ids = ctype.SField(ctype.c_int32, 0X3C)
    layer_id_count = ctype.SField(ctype.c_int32, 0X40)

    @functools.cached_property
    def layer_ids(self):
        return (ctype.c_uint8 * self.layer_id_count)(_address_=self._address_ + self._layer_ids)


class PrefetchRangeInstanceObject(TriggerBoxInstanceObject):
    bound_instance_id = ctype.SField(ctype.c_uint32, 0X3C)


class RestBonusRangeInstanceObject(TriggerBoxInstanceObject):
    pass


class DoorRangeInstanceObject(TriggerBoxInstanceObject):
    pass


class MapRangeInstanceObject(TriggerBoxInstanceObject):
    map = ctype.SField(ctype.c_uint32, 0X3C)
    place_name_block = ctype.SField(ctype.c_uint32, 0X40)
    place_name_spot = ctype.SField(ctype.c_uint32, 0X44)
    weather = ctype.SField(ctype.c_uint32, 0X48)
    bgm = ctype.SField(ctype.c_uint32, 0X4C)
    game_collision_enabled = ctype.SField(ctype.c_int8, 0X58)
    housing_area_id = ctype.SField(ctype.c_uint8, 0X59)
    housing_block_id = ctype.SField(ctype.c_uint8, 0X5A)
    rest_bonus_effective = ctype.SField(ctype.c_int8, 0X5B)
    discovery_id = ctype.SField(ctype.c_uint8, 0X5C)
    map_enabled = ctype.SField(ctype.c_int8, 0X5D)
    place_name_enabled = ctype.SField(ctype.c_int8, 0X5E)
    discovery_enabled = ctype.SField(ctype.c_int8, 0X5F)
    bgm_enabled = ctype.SField(ctype.c_int8, 0X60)
    weather_enabled = ctype.SField(ctype.c_int8, 0X61)
    rest_bonus_enabled = ctype.SField(ctype.c_int8, 0X62)
    bgm_play_zone_in_only = ctype.SField(ctype.c_int8, 0X63)
    lift_enabled = ctype.SField(ctype.c_int8, 0X64)
    housing_enabled = ctype.SField(ctype.c_int8, 0X65)
    notification_enabled = ctype.SField(ctype.c_int8, 0X66)
    unflyable_enabled = ctype.SField(ctype.c_int8, 0X67)
    mount_disabled = ctype.SField(ctype.c_int8, 0X68)
    race_enter__lalafell = ctype.SField(ctype.c_int8, 0X69)


class ExitRangeInstanceObject(TriggerBoxInstanceObject):
    class ExitType(enum.IntEnum):
        ExitTypeZone = 0X1
        ExitTypeWarp = 0X2

    exit_type = ctype.SField(ctype.c_int32, 0X3C)
    zone_id = ctype.SField(ctype.c_uint16, 0X40)
    territory_type = ctype.SField(ctype.c_uint16, 0X42)
    index = ctype.SField(ctype.c_int32, 0X44)
    dest_instance_id = ctype.SField(ctype.c_uint32, 0X48)
    return_instance_id = ctype.SField(ctype.c_uint32, 0X4C)
    player_running_direction = ctype.SField(ctype.c_float, 0X50)
    ex_data_id = ctype.SField(ctype.c_uint16, 0X54)
    dest_instance_id_for_flying = ctype.SField(ctype.c_uint32, 0X58)

    @property
    def e_exit_type(self):
        return self.ExitType(self.exit_type)


class FateRangeInstanceObject(TriggerBoxInstanceObject):
    fate_layout_label_id = ctype.SField(ctype.c_uint32, 0X3C)


class GameContentsRangeInstanceObject(TriggerBoxInstanceObject):
    test_enabled = ctype.SField(ctype.c_int8, 0X40)
