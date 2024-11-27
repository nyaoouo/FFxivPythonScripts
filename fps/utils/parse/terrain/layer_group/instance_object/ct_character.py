import enum
from .utils import *


class CTCharacter(InstanceObject):
    flags = ctype.SField(ctype.c_uint32, 0X30)
    e_npc_id = ctype.SField(ctype.c_uint32, 0X34)
    b_npc_id = ctype.SField(ctype.c_uint32, 0X38)
    se_pack = ctype.SField(ctype.c_uint32, 0X3C)
    _model_visibilities = ctype.SField(ctype.c_int32, 0X40)
    model_visibility_count = ctype.SField(ctype.c_int32, 0X44)
    _weapons = ctype.SField(ctype.c_int32, 0X48)
    weapon_count = ctype.SField(ctype.c_int32, 0X4C)
    visible = ctype.SField(ctype.c_int8, 0X50)

    @functools.cached_property
    def model_visibilities(self):
        return (ctype.c_uint8 * self.model_visibility_count)(_address_=self._address_ + self._model_visibilities)

    @functools.cached_property
    def weapons(self):
        return (ctype.c_uint8 * self.weapon_count)(_address_=self._address_ + self._weapons)


class CTMonster(CTCharacter):
    primary_model_id = ctype.SField(ctype.c_uint16, 0X54)
    secondary_model_id = ctype.SField(ctype.c_uint16, 0X56)
    image_change_id = ctype.SField(ctype.c_uint16, 0X58)
    material_id = ctype.SField(ctype.c_uint32, 0X5C)
    decal_id = ctype.SField(ctype.c_uint32, 0X60)
    vfx_id = ctype.SField(ctype.c_uint32, 0X64)
    material_animation_id = ctype.SField(ctype.c_uint32, 0X68)


class CTEquipmentElement(ctype.Struct):
    _size_ = 0X20
    image_change_id = ctype.SField(ctype.c_uint32, 0X0)
    equipment_id = ctype.SField(ctype.c_uint32, 0X4)
    staining_id = ctype.SField(ctype.c_uint32, 0X8)
    free_company = ctype.SField(ctype.c_uint32, 0XC)
    material_id = ctype.SField(ctype.c_uint32, 0X10)
    decal_id = ctype.SField(ctype.c_uint32, 0X14)
    vfx_id = ctype.SField(ctype.c_uint32, 0X18)
    material_animation_id = ctype.SField(ctype.c_uint32, 0X1C)


class CTWeapon(CTCharacter):
    primary_model_id = ctype.SField(ctype.c_uint16, 0X54)
    secondary_model_id = ctype.SField(ctype.c_uint16, 0X56)
    image_change_id = ctype.SField(ctype.c_uint16, 0X58)
    staining_id = ctype.SField(ctype.c_uint16, 0X5A)
    material_id = ctype.SField(ctype.c_uint32, 0X5C)
    free_company = ctype.SField(ctype.c_uint32, 0X60)
    decal_id = ctype.SField(ctype.c_uint32, 0X64)
    vfx_id = ctype.SField(ctype.c_uint32, 0X68)
    material_animation_id = ctype.SField(ctype.c_uint32, 0X6C)
    attach_type = ctype.SField(ctype.c_int32, 0X70)


class AccessorySlot(enum.IntEnum):
    EARRING = 0X0
    NECKLACE = 0X1
    WRIST = 0X2
    FINGER_R = 0X3
    FINGER_L = 0X4


class ArmorSlot(enum.IntEnum):
    HELMET = 0X0
    TOP = 0X1
    GLOVE = 0X2
    DOWN = 0X3
    SHOES = 0X4


class ModelSlot(enum.IntEnum):
    HELMET = 0X0
    TOP = 0X1
    GLOVE = 0X2
    DOWN = 0X3
    SHOES = 0X4
    EARRING = 0X5
    NECKLACE = 0X6
    WRIST = 0X7
    FINGER_R = 0X8
    FINGER_L = 0X9
    HAIR = 0XA
    FACE = 0XB
    TAIL = 0XC
    CONNECTION_SUPER = 0XD
    CONNECTION = 0XE


class CTHuman(CTCharacter):
    _armor_elements = ctype.SField(ctype.c_int32, 0X54)
    armor_element_count = ctype.SField(ctype.c_int32, 0X58)

    @functools.cached_property
    def armor_elements(self):
        return (CTEquipmentElement * self.armor_element_count)(_address_=self._address_ + self._armor_elements)


class CTPlayer(CTHuman):
    _customize_data = ctype.SField(ctype.c_int32, 0X5C)
    customize_data_count = ctype.SField(ctype.c_int32, 0X60)
    _accessory_elements = ctype.SField(ctype.c_int32, 0X64)
    accessory_element_count = ctype.SField(ctype.c_int32, 0X68)
    hair_material_id = ctype.SField(ctype.c_uint32, 0X6C)

    @functools.cached_property
    def customize_data(self):
        return (ctype.c_uint8 * self.customize_data_count)(_address_=self._address_ + self._customize_data)

    @functools.cached_property
    def accessory_elements(self):
        return (CTEquipmentElement * self.accessory_element_count)(_address_=self._address_ + self._accessory_elements)


class CTDemiHuman(CTHuman):
    skeleton_id = ctype.SField(ctype.c_uint32, 0X5C)
