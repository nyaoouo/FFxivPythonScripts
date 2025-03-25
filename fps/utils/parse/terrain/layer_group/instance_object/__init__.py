import struct
from nylib import ctype

from .utils import InstanceObject
from . import ct_character, game_object, helper_object, trigger_box, pop_range, bg, vfx, shared_group
from . import env
from ..utils import AssetType

# TODO

instance_object_map = {
    AssetType.BG: bg.BGInstanceObject,
    AssetType.Attribute: None,
    AssetType.LayLight: None,
    AssetType.VFX: vfx.VFXInstanceObject,
    AssetType.PositionMarker: None,
    AssetType.SharedGroup: shared_group.SGInstanceObject,
    AssetType.Sound: None,
    AssetType.EventNPC: game_object.ENPCInstanceObject,
    AssetType.BattleNPC: game_object.BNPCInstanceObject,
    AssetType.RoutePath: None,
    AssetType.Character: ct_character.CTCharacter,
    AssetType.Aetheryte: game_object.AetheryteInstanceObject,
    AssetType.EnvSet: env.EnvSetInstanceObject,
    AssetType.Gathering: game_object.GatheringInstanceObject,
    AssetType.HelperObject: helper_object.HelperObjInstanceObject,
    AssetType.Treasure: game_object.TreasureInstanceObject,
    AssetType.Clip: None,
    AssetType.ClipCtrlPoint: None,
    AssetType.ClipCamera: None,
    AssetType.ClipLight: None,
    AssetType.ClipPathCtrlPoint: None,
    AssetType.CutAssetOnlySelectable: None,
    AssetType.Player: ct_character.CTPlayer,
    AssetType.Monster: ct_character.CTMonster,
    AssetType.Weapon: ct_character.CTWeapon,
    AssetType.PopRange: pop_range.PopRangeInstanceObject,
    AssetType.ExitRange: trigger_box.ExitRangeInstanceObject,
    AssetType.LVB: None,
    AssetType.MapRange: trigger_box.MapRangeInstanceObject,
    AssetType.NavMeshRange: None,
    AssetType.EventObject: game_object.EventInstanceObject,
    AssetType.DemiHuman: ct_character.CTDemiHuman,
    AssetType.EnvLocation: env.EnvLocationInstanceObject,
    AssetType.ControlPoint: None,
    AssetType.EventRange: trigger_box.EventRangeInstanceObject,
    AssetType.RestBonusRange: trigger_box.RestBonusRangeInstanceObject,
    AssetType.QuestMarker: None,
    AssetType.Timeline: None,
    AssetType.ObjectBehaviorSet: None,
    AssetType.Movie: None,
    AssetType.ScenarioEXD: None,
    AssetType.ScenarioText: None,
    AssetType.CollisionBox: trigger_box.CollisionBoxInstanceObject,
    AssetType.DoorRange: trigger_box.DoorRangeInstanceObject,
    AssetType.LineVFX: None,
    AssetType.SoundEnvSet: None,
    AssetType.CutActionTimeline: None,
    AssetType.CharaScene: None,
    AssetType.CutAction: None,
    AssetType.EquipPreset: None,
    AssetType.ClientPath: None,
    AssetType.ServerPath: None,
    AssetType.GimmickRange: trigger_box.GimmickRangeInstanceObject,
    AssetType.TargetMarker: None,
    AssetType.ChairMarker: None,
    AssetType.ClickableRange: trigger_box.ClickableRangeInstanceObject,
    AssetType.PrefetchRange: trigger_box.PrefetchRangeInstanceObject,
    AssetType.FateRange: trigger_box.FateRangeInstanceObject,
    AssetType.PartyMember: None,
    AssetType.KeepRange: None,
    AssetType.SphereCastRange: trigger_box.SphereCastRangeInstanceObject,
    AssetType.IndoorObject: None,
    AssetType.OutdoorObject: None,
    AssetType.EditGroup: None,
    AssetType.StableChocobo: None,
    AssetType.GroomPlayer: None,
    AssetType.BridePlayer: None,
    AssetType.WeddingGuestPlayer: None,
    AssetType.Decal: None,
    AssetType.SystemActor: None,
    AssetType.CustomSharedGroup: None,
    AssetType.WaterRange: trigger_box.WaterRangeInstanceObject,
    AssetType.ShowHideRange: trigger_box.ShowHideRangeInstanceObject,
    AssetType.GameContentsRange: trigger_box.GameContentsRangeInstanceObject,
    AssetType.EventEffectRange: trigger_box.EventEffectRangeInstanceObject,
}


def get_instance_object(buf, off=0) -> InstanceObject:
    return ctype.cdata_from_buffer(buf, instance_object_map.get(struct.unpack_from(b'I', buf, off)[0]) or InstanceObject, off)


def get_instance_object_from_addr(addr) -> InstanceObject:
    return (instance_object_map.get(ctype.c_int32(_address_=addr).value) or InstanceObject)(_address_=addr)
