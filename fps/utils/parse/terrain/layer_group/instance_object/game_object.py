from .utils import *

class GameInstanceObject(InstanceObject):
    base_id = ctype.SField(ctype.c_uint32, 0X30)


class NPCInstanceObject(GameInstanceObject):
    pop_weather = ctype.SField(ctype.c_uint32, 0X34)
    pop_time_start = ctype.SField(ctype.c_uint8, 0X38)
    pop_time_end = ctype.SField(ctype.c_uint8, 0X39)
    padding00 = ctype.Field(ctype.c_uint8 * 2, 0X3A)
    move_ai = ctype.SField(ctype.c_uint32, 0X3C)
    wandering_range = ctype.SField(ctype.c_uint8, 0X40)
    route = ctype.SField(ctype.c_uint8, 0X41)
    event_group = ctype.SField(ctype.c_uint16, 0X42)




class BNpcBaseData(ctype.Struct):
    _size_ = 0X8
    territory_range = ctype.SField(ctype.c_uint16, 0X0)
    sense = ctype.Field(ctype.c_uint8 * 2, 0X2)
    sense_range = ctype.Field(ctype.c_uint8 * 2, 0X4)
    mount = ctype.SField(ctype.c_uint8, 0X6)


class BNPCInstanceObject(NPCInstanceObject):
    name_id = ctype.SField(ctype.c_uint32, 0X4C)
    drop_item = ctype.SField(ctype.c_uint32, 0X50)
    sense_range_rate = ctype.SField(ctype.c_float, 0X54)
    level = ctype.SField(ctype.c_uint16, 0X58)
    active_type = ctype.SField(ctype.c_uint8, 0X5A)
    pop_interval = ctype.SField(ctype.c_uint8, 0X5B)
    pop_rate = ctype.SField(ctype.c_uint8, 0X5C)
    pop_event = ctype.SField(ctype.c_uint8, 0X5D)
    link_group = ctype.SField(ctype.c_uint8, 0X5E)
    link_family = ctype.SField(ctype.c_uint8, 0X5F)
    link_range = ctype.SField(ctype.c_uint8, 0X60)
    link_count_limit = ctype.SField(ctype.c_uint8, 0X61)
    nonpop_init_zone = ctype.SField(ctype.c_int8, 0X62)
    invalid_repop = ctype.SField(ctype.c_int8, 0X63)
    link_parent = ctype.SField(ctype.c_int8, 0X64)
    link_override = ctype.SField(ctype.c_int8, 0X65)
    link_reply = ctype.SField(ctype.c_int8, 0X66)
    nonpop = ctype.SField(ctype.c_int8, 0X67)
    relative_positions: 'RelativePositions' = eval('0X68')
    horizontal_pop_range = ctype.SField(ctype.c_float, 0X70)
    vertical_pop_range = ctype.SField(ctype.c_float, 0X74)
    _b_npc_base_data = ctype.SField(ctype.c_int32, 0X78)
    repop_id = ctype.SField(ctype.c_uint8, 0X7C)
    bnpc_rank_id = ctype.SField(ctype.c_uint8, 0X7D)
    territory_range = ctype.SField(ctype.c_uint16, 0X7E)
    bound_instance_id = ctype.SField(ctype.c_uint32, 0X80)
    fate_layout_label_id = ctype.SField(ctype.c_uint32, 0X84)
    normal_ai = ctype.SField(ctype.c_uint32, 0X88)
    server_path_id = ctype.SField(ctype.c_uint32, 0X8C)
    equipment_id = ctype.SField(ctype.c_uint32, 0X90)
    customize_id = ctype.SField(ctype.c_uint32, 0X94)

    @functools.cached_property
    def b_npc_base_data(self):
        return BNpcBaseData(_address_=self._address_ + self._b_npc_base_data)


class ENPCInstanceObject(NPCInstanceObject):
    behavior = ctype.SField(ctype.c_uint32, 0X4C)
    mount_id = ctype.SField(ctype.c_uint32, 0X50)
    aerial_access = ctype.SField(ctype.c_int8, 0X54)
    disable_hum = ctype.SField(ctype.c_int8, 0X55)


class GatheringInstanceObject(GameInstanceObject):
    pass


class AetheryteInstanceObject(GameInstanceObject):
    bound_instance_id = ctype.SField(ctype.c_uint32, 0X34)


class EventInstanceObject(GameInstanceObject):
    bound_instance_id = ctype.SField(ctype.c_uint32, 0X34)
    linked_instance_id = ctype.SField(ctype.c_uint32, 0X38)
    aerial_access = ctype.SField(ctype.c_int8, 0X3C)
    disable_error_check = ctype.SField(ctype.c_int8, 0X3D)


class TreasureInstanceObject(GameInstanceObject):
    nonpop_init_zone = ctype.SField(ctype.c_int8, 0X34)
