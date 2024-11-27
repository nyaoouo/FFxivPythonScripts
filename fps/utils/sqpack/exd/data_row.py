import typing
from typing import Generic, TypeVar, TYPE_CHECKING, Callable, Tuple, Type, Iterable

from nylib.utils import Counter
from ..utils import Language, icon_path

if TYPE_CHECKING:
    from .row import DataRow
    from ..pack import PackManager

_T = TypeVar("_T")
counter = Counter()


class SimpleData(Generic[_T]):
    def __init__(self, col_id: int):
        self.col_id = col_id

    def __get__(self, instance, owner) -> _T:
        return instance[self.col_id]


class ColorData:
    def __init__(self, col_id: int, include_alpha: bool = True):
        self.col_id = col_id
        self.include_alpha = include_alpha

    @classmethod
    def make(cls, include_alpha: bool = True):
        def wrapper(col_id: int):
            return cls(col_id, include_alpha)

        return wrapper

    def __get__(self, instance, owner) -> Tuple[int, int, int, int]:
        val = instance[self.col_id]
        if not self.include_alpha:
            return (val >> 16) & 0xff >> 16, (val >> 8) & 0xff >> 8, val & 0xff, 1
        return (val >> 16) & 0xff >> 16, (val >> 8) & 0xff >> 8, val & 0xff, (val >> 24) & 0xff


class LinkData(Generic[_T]):
    def __init__(self, col_id: int, sheet_name):
        self.col_id = col_id
        self.sheet_name = sheet_name
        self.cache_key = f'__cached_{counter.get()}'

    @classmethod
    def make(cls, sheet_name: str):
        def wrapper(col_id: int):
            return cls(col_id, sheet_name)

        return wrapper

    def __get__(self, instance: 'DataRow', owner) -> _T | int | None:
        if not hasattr(instance, self.cache_key):
            sheet = instance.row_base.sheet.mgr.get_sheet_raw(self.sheet_name)
            key = instance[self.col_id]
            try:
                lang = instance.row_base.lang_sheet.lang
                item = sheet.get_row(key, lang if lang.value else None)
            except KeyError:
                item = key
            setattr(instance, self.cache_key, item)
        return getattr(instance, self.cache_key, None)


class IconData_:
    def __init__(self, instance: 'DataRow', icon_id: int):
        self._instance = instance
        self.icon_id = icon_id

    def get_image(self, is_hq=False):
        row_base = self._instance.row_base
        lang = row_base.lang_sheet.lang
        lang = lang.name if isinstance(lang, Language) and lang.value else None
        pm = row_base.sheet.mgr.pack
        try:
            file = pm.get_texture_file(icon_path(self.icon_id, is_hq, lang))
        except FileNotFoundError:
            if lang is not None:
                file = pm.get_texture_file(icon_path(self.icon_id, is_hq))
            else:
                raise
        return file.get_image()


class IconData:
    def __init__(self, col_id: int):
        self.col_id = col_id

    def __get__(self, instance, owner) -> 'IconData_|None':
        if id_ := instance[self.col_id]:
            return IconData_(instance, id_)


class ArrayData_(Generic[_T]):
    def __init__(self, instance: 'DataRow', accessors):
        self._instance = instance
        self._accessors = accessors

    def __len__(self):
        return len(self._accessors)

    @typing.overload
    def __getitem__(self, item: int) -> _T:
        ...

    @typing.overload
    def __getitem__(self, item: slice) -> Tuple[_T, ...]:
        ...

    def __getitem__(self, item):
        if isinstance(item, slice):
            return tuple(self._accessors[i] for i in range(*item.indices(len(self))))
        return self._accessors[item].__get__(self._instance, None)


class ArrayData(Generic[_T]):
    def __init__(self, col_id: int, size: int, sep: int, el_type: 'Callable[[int], Generic[_T]]'):
        self.accessors = []
        for i in range(size):
            self.accessors.append(el_type(col_id + i * sep))

    @classmethod
    def make(cls, size: int, sep: int, el_type: 'Callable[[int], Generic[_T]]') -> 'Callable[[int], ArrayData[_T]]':
        def wrapper(col_id: int):
            return cls(col_id, size, sep, el_type)

        return wrapper

    def __get__(self, instance, owner) -> ArrayData_[_T]:
        return ArrayData_(instance, self.accessors)


class Struct:
    def __init__(self, instance, col_id: int):
        self._instance = instance
        self._col_id = col_id

    def __getitem__(self, item: int):
        return self._instance[self._col_id + item]


class StructData(Generic[_T]):
    def __init__(self, col_id: int, el_type: Type[_T]):
        self.col_id = col_id
        self.el_type = el_type

    @classmethod
    def make(cls, el_type: Type[_T]) -> Callable[[int], 'StructData[_T]']:
        def wrapper(col_id):
            return cls(col_id, el_type)

        return wrapper

    def __get__(self, instance, owner) -> _T:
        return self.el_type(instance, self.col_id)
