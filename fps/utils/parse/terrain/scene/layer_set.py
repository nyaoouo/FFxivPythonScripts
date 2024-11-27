import ctypes
import functools

from nylib import ctype
from ..utils import offset_string


class LayerReference(ctype.Struct):
    _size_ = 0X8
    layer_id = ctype.SField(ctype.c_uint32, 0X0)


class LayerSet(ctype.Struct):
    _size_ = 0X1C
    _nav_mesh_asset_path = ctype.SField(ctype.c_int32, 0X0)
    layer_set_id = ctype.SField(ctype.c_uint32, 0X4)
    _layer_references = ctype.SField(ctype.c_int32, 0X8)
    layer_reference_count = ctype.SField(ctype.c_int32, 0XC)
    territory_type_id = ctype.SField(ctype.c_uint16, 0X10)
    content_finder_condition_id = ctype.SField(ctype.c_uint16, 0X12)
    _name = ctype.SField(ctype.c_int32, 0X14)
    _nav_mesh_ex_asset_path = ctype.SField(ctype.c_int32, 0X18)

    nav_mesh_asset_path = offset_string('_navi_mesh_asset_path')
    name = offset_string('_name')
    nav_mesh_ex_asset_path = offset_string('_nav_mesh_ex_asset_path')

    @functools.cached_property
    def layer_references(self):
        return (LayerReference * self.layer_reference_count)(_address_=self._address_ + self._layer_references)


class LayerSetFolder(ctype.Struct):
    _size_ = 0X8
    _layer_sets = ctype.SField(ctype.c_int32, 0X0)
    layer_set_count = ctype.SField(ctype.c_int32, 0X4)

    # @functools.cached_property
    @property
    def layer_sets(self):
        return (LayerSet * self.layer_set_count)(_address_=self._address_ + self._layer_sets)
