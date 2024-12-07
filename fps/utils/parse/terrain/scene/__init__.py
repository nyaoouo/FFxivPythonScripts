import ctypes
import functools
import logging
import typing

from nylib import ctype
from .layer_set import LayerSetFolder
from .sg_timeline import SGTimelineFolder
from .sg_settings import SGSettings
from .housing_settings import HousingSettings
from ..layer_group import LayerGroup
from ..utils import find_binary_by_chunk_id, offset_string

if typing.TYPE_CHECKING:
    from fps.utils.sqpack import SqPack


class SceneSettings(ctype.Struct):
    is_partial_output = ctype.SField(ctype.c_int8, 0X0)
    contains_layer_set_ref = ctype.SField(ctype.c_int8, 0X1)
    is_dungeon = ctype.SField(ctype.c_int8, 0X2)
    exists_grass_data = ctype.SField(ctype.c_int8, 0X3)
    _terrain_asset_path = ctype.SField(ctype.c_int32, 0X4)
    env_set_attr_references = ctype.SField(ctype.c_int32, 0X8)
    env_set_attr_reference__count = ctype.SField(ctype.c_int32, 0XC)
    sunrise_angle = ctype.SField(ctype.c_int32, 0X10)
    sky_visibility_path = ctype.SField(ctype.c_int32, 0X14)
    camera_far_clip_distance = ctype.SField(ctype.c_float, 0X18)
    main_light_orbit_curve = ctype.SField(ctype.c_float, 0X1C)
    main_light_orbit_clamp = ctype.SField(ctype.c_float, 0X20)
    shadow_far_distance = ctype.SField(ctype.c_float, 0X24)
    shadow_distance_fade = ctype.SField(ctype.c_float, 0X28)
    bg_sky_visibility = ctype.SField(ctype.c_float, 0X2C)
    bg_material_color = ctype.SField(ctype.c_int32, 0X30)
    light_clip_aabb_path = ctype.SField(ctype.c_int32, 0X34)
    terrain_occlusion_rain_enabled = ctype.SField(ctype.c_int8, 0X38)
    terrain_occlusion_dust_enabled = ctype.SField(ctype.c_int8, 0X39)
    constant_time_mode_enabled = ctype.SField(ctype.c_int8, 0X3A)
    constant_time = ctype.SField(ctype.c_float, 0X3C)
    level_weather_table = ctype.SField(ctype.c_int32, 0X40)
    sky_horizon = ctype.SField(ctype.c_float, 0X44)
    waving_anime_time_scale = ctype.SField(ctype.c_float, 0X48)
    is_underwater = ctype.SField(ctype.c_int8, 0X4C)
    is_all_celestial_sphere = ctype.SField(ctype.c_int8, 0X4D)
    shadow_distance_scale_in_flying = ctype.SField(ctype.c_float, 0X50)
    terrain_asset_path = offset_string('_terrain_asset_path')


class Scene(ctype.Struct):
    LV_SCENE = b'LVB1'
    SG_SCENE = b'SGB1'
    path = None

    @classmethod
    def lv_scene(cls, sq_pack: 'SqPack', territory_id: int):
        return cls.get(sq_pack, b'bg/%s.lvb' % sq_pack.sheets.territory_type_sheet[territory_id].lvb.encode(), cls.LV_SCENE)

    @classmethod
    def get(cls, sq_pack: 'SqPack', path, file_id: bytes) -> 'Scene|None':
        k = '__cached_scene_' + file_id.decode()
        if (c := getattr(sq_pack, k, None)) is None: setattr(sq_pack, k, c := {})
        if path not in c:
            try:
                buf = memoryview(sq_pack.pack.get_file(path).data_buffer)
            except FileNotFoundError:
                _logger.warning(f'file not found {path}')
                c[path] = res = None
            else:
                c[path] = res = ctype.cdata_from_buffer(find_binary_by_chunk_id(buf, b'SCN1', file_id), cls)
                res.path = path
            return res
        return c[path]

    _layer_groups = ctype.SField(ctype.c_int32, 0X0)
    layer_group_count = ctype.SField(ctype.c_int32, 0X4)
    _settings = ctype.SField(ctype.c_int32, 0X8)
    _layer_set_folder = ctype.SField(ctype.c_int32, 0XC)
    _sg_timeline_folder = ctype.SField(ctype.c_int32, 0X10)
    _lgb_asset_paths = ctype.SField(ctype.c_int32, 0X14)
    lgb_asset_path_count = ctype.SField(ctype.c_int32, 0X18)
    sg_door_settings = ctype.SField(ctype.c_int32, 0X1C)
    _sg_settings = ctype.SField(ctype.c_int32, 0X20)
    sg_rotation_settings = ctype.SField(ctype.c_int32, 0X24)
    sg_random_timeline_settings = ctype.SField(ctype.c_int32, 0X28)
    _housing_settings = ctype.SField(ctype.c_int32, 0X2C)
    sg_clock_settings = ctype.SField(ctype.c_int32, 0X30)

    @functools.cached_property
    def setting(self):
        return SceneSettings(_address_=self._address_ + self._settings)

    @functools.cached_property
    def lgb_asset_paths(self):
        p_offset = self._address_ + self._lgb_asset_paths
        return [ctypes.string_at(p_offset + o) for o in (ctype.c_int32 * self.lgb_asset_path_count)(_address_=p_offset)]

    @functools.cached_property
    def layer_groups(self):
        return (LayerGroup * self.layer_group_count)(_address_=self._address_ + self._layer_groups)

    @functools.cached_property
    def layer_sets(self):
        return LayerSetFolder(_address_=self._address_ + self._layer_set_folder).layer_sets

    @functools.cached_property
    def sg_timelines(self):
        return SGTimelineFolder(_address_=self._address_ + self._sg_timeline_folder).sg_timelines

    @functools.cached_property
    def sg_settings(self):
        return SGSettings(_address_=self._address_ + self._sg_settings)

    @functools.cached_property
    def housing_settings(self):
        return HousingSettings(_address_=self._address_ + self._housing_settings)


_logger = logging.getLogger('LayerGroup')
