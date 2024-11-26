from pathlib import Path
from .pack import PackManager
from .exd import ExdManager
from .utils import Language

_cached_sqpack = {}


class SqPack:
    _is_init = False

    def __new__(cls, game_path: str | Path = None, default_language: Language = Language.en, exd_keep_in_memory=True):
        if game_path is None: return next(iter(_cached_sqpack.values()))
        game_path = (Path(game_path) if isinstance(game_path, str) else game_path).absolute()
        if sqpack := _cached_sqpack.get((game_path, default_language)): return sqpack
        return super().__new__(cls)

    def __init__(self, game_path: str | Path, default_language: Language = Language.en, exd_keep_in_memory=True):
        if self._is_init: return
        _cached_sqpack[game_path, default_language] = self
        self.game_path = game_path if isinstance(game_path, Path) else Path(game_path)
        self.pack = PackManager(self.game_path / 'sqpack')
        self.exd = ExdManager(self.pack, default_language=default_language, exd_keep_in_memory=exd_keep_in_memory)
        self._is_init = True
