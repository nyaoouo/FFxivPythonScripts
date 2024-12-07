import ctypes
import functools
import logging
import typing

from nylib import ctype
from .utils import AssetType
from .instance_object import get_instance_object_from_addr
from ..utils import find_binary_by_chunk_id, offset_string

if typing.TYPE_CHECKING:
    from fps.utils.sqpack import SqPack


class OBSetEnableReferenced(ctype.Struct):
    _size_ = 0XC
    asset_type = ctype.SField(ctype.c_uint32, 0X0)
    instance_id = ctype.SField(ctype.c_uint32, 0X4)
    ob_set_enable = ctype.SField(ctype.c_int8, 0X8)
    ob_set_emissive_enable = ctype.SField(ctype.c_int8, 0X9)

    @property
    def e_asset_type(self):
        return AssetType(self.asset_type)


class OBSetReferenced(ctype.Struct):
    _size_ = 0XC

    asset_type = ctype.SField(ctype.c_uint32, 0X0)
    instance_id = ctype.SField(ctype.c_uint32, 0X4)
    _ob_set_asset_path = ctype.SField(ctype.c_int32, 0X8)

    @property
    def e_asset_type(self):
        return AssetType(self.asset_type)

    ob_set_asset_path = offset_string('_ob_set_asset_path')


class Layer(ctype.Struct):
    _size_ = 0X34
    layer_id = ctype.SField(ctype.c_uint32, 0X0)
    _name = ctype.SField(ctype.c_int32, 0X4)
    _instance_objects = ctype.SField(ctype.c_int32, 0X8)
    instance_object_count = ctype.SField(ctype.c_int32, 0XC)
    tool_mode_visible = ctype.SField(ctype.c_int8, 0X10)
    tool_mode_read_only = ctype.SField(ctype.c_int8, 0X11)
    is_bush_layer = ctype.SField(ctype.c_int8, 0X12)
    ps3_visible = ctype.SField(ctype.c_int8, 0X13)
    layer_set_ref = ctype.SField(ctype.c_int32, 0X14)
    festival_id = ctype.SField(ctype.c_uint16, 0X18)
    festival_phase_id = ctype.SField(ctype.c_uint16, 0X1A)
    is_temporary = ctype.SField(ctype.c_int8, 0X1C)
    is_housing = ctype.SField(ctype.c_int8, 0X1D)
    version_mask = ctype.SField(ctype.c_uint16, 0X1E)
    housing_area_id = ctype.SField(ctype.c_uint8, 0X20)
    reserved1 = ctype.SField(ctype.c_uint8, 0X21)
    reserved2 = ctype.SField(ctype.c_uint16, 0X22)
    _ob_set_referenced_list = ctype.SField(ctype.c_int32, 0X24)
    ob_set_referenced_list_count = ctype.SField(ctype.c_int32, 0X28)
    _ob_set_enable_referenced_list = ctype.SField(ctype.c_int32, 0X2C)
    ob_set_enable_referenced_list_count = ctype.SField(ctype.c_int32, 0X30)

    name = offset_string('_name')

    @functools.cached_property
    def instance_objects(self):
        p_offset = self._address_ + self._instance_objects
        return [
            get_instance_object_from_addr(p_offset + o)
            for o in (ctype.c_int32 * self.instance_object_count)(_address_=p_offset)
        ]

    @functools.cached_property
    def ob_set_referenced_list(self):
        return (OBSetReferenced * self.ob_set_referenced_list_count)(_address_=self._address_ + self._ob_set_referenced_list)

    @functools.cached_property
    def ob_set_enable_referenced_list(self):
        return (OBSetReferenced * self.ob_set_enable_referenced_list_count).from_address(
            self._address_ + self._ob_set_enable_referenced_list
        )


class LayerGroup(ctype.Struct):
    _size_ = 0X10
    layer_group_id = ctype.SField(ctype.c_uint32, 0X0)
    _name = ctype.SField(ctype.c_int32, 0X4)
    _layers = ctype.SField(ctype.c_int32, 0X8)
    layer_count = ctype.SField(ctype.c_int32, 0XC)

    name = offset_string('_name')
    path = None

    @classmethod
    def get(cls, sq_pack: 'SqPack', path) -> 'LayerGroup|None':
        if (c := getattr(sq_pack, '__cached_layer_group', None)) is None:
            setattr(sq_pack, '__cached_layer_group', c := {})
        if path not in c:
            try:
                buf = memoryview(sq_pack.pack.get_file(path).data_buffer)
            except FileNotFoundError:
                _logger.warning(f'file not found {path}')
                c[path] = res = None
            else:
                # c[path] = res = cls.from_buffer(find_binary_by_chunk_id(buf, b'LGP1', b'LGB1'))
                c[path] = res = ctype.cdata_from_buffer(find_binary_by_chunk_id(buf, b'LGP1', b'LGB1'), cls)
                res.path = path
            return res
        return c[path]

    @functools.cached_property
    def layers(self):
        p_offset = self._address_ + self._layers
        return [Layer(_address_=p_offset + o) for o in (ctype.c_int32 * self.layer_count)(_address_=p_offset)]


_logger = logging.getLogger('LayerGroup')
