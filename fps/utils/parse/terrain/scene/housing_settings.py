import ctypes
import enum
import functools

from nylib import ctype
from nylib.utils.enum import auto_missing
from ..utils import offset_string


@auto_missing
class HousingSizeType(enum.IntEnum):
    S = 0X0
    M = 0X1
    L = 0X2


@auto_missing
class HousingTimelinePlayType(enum.IntEnum):
    Switch = 0X0
    Trigger = 0X1


@auto_missing
class HousingCraftType(enum.IntEnum):
    Null = 0X0
    AetherialWheel = 0X1
    House = 0X2
    Airship = 0X3
    Submarine = 0X4


@auto_missing
class HounsingCombinedFurnitureType(enum.IntEnum):
    Null = 0X0
    Gardening = 0X1
    AetherialWheel = 0X2
    EmploymentNPC = 0X3
    ChocoboStable = 0X4
    FishPrint = 0X5
    Picture = 0X6
    Wallpaper = 0X7
    Flowerpot = 0X8
    Aquarium = 0X9
    AquariumParts = 0XA


class HousingCombinedFurnitureSettings(ctype.Struct):
    combined_furniture_type = ctype.SField(ctype.c_int32, 0X0)
    slot_member_ids = ctype.Field(ctype.c_uint32 * 8, 0X4)

    @property
    def e_combined_furniture_type(self):
        return HounsingCombinedFurnitureType(self.combined_furniture_type)


class HousingLayoutAttribute(ctype.Struct):
    wall = ctype.SField(ctype.c_int8, 0X0)
    table = ctype.SField(ctype.c_int8, 0X1)
    desktop = ctype.SField(ctype.c_int8, 0X2)
    wall_hung = ctype.SField(ctype.c_int8, 0X3)
    window = ctype.SField(ctype.c_int8, 0X4)


class HousingSettings(ctype.Struct):
    default_color_id = ctype.SField(ctype.c_uint16, 0X0)
    block_id = ctype.SField(ctype.c_uint8, 0X2)
    block_size = ctype.SField(ctype.c_int32, 0X4)
    groups = ctype.SField(ctype.c_int32, 0X20)
    group_count = ctype.SField(ctype.c_int32, 0X24)
    _ob_set_asset_path = ctype.SField(ctype.c_int32, 0X28)
    _combined_furniture_settings = ctype.SField(ctype.c_int32, 0X2C)
    _layout_attribute = ctype.SField(ctype.c_int32, 0X30)
    initial_emissive_state = ctype.SField(ctype.c_int8, 0X34)
    timeline_play_type = ctype.SField(ctype.c_int32, 0X38)
    housing_craft_type = ctype.SField(ctype.c_int32, 0X3C)
    base_scale = ctype.SField(ctype.c_float, 0X40)

    ob_set_asset_path = offset_string('_ob_set_asset_path')

    @property
    def e_block_size(self):
        return HousingSizeType(self.block_size)

    @property
    def e_timeline_play_type(self):
        return HousingTimelinePlayType(self.timeline_play_type)

    @property
    def e_housing_craft_type(self):
        return HousingCraftType(self.housing_craft_type)

    @functools.cached_property
    def combined_furniture_settings(self):
        return HousingCombinedFurnitureSettings(_address_=self._address_ + self._combined_furniture_settings)

    @functools.cached_property
    def layout_attribute(self):
        return HousingLayoutAttribute(_address_=self._address_ + self._layout_attribute)
