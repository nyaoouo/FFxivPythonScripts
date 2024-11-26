import typing
from typing import Generic, TypeVar, TYPE_CHECKING, Callable, Tuple, Type, Iterable

if TYPE_CHECKING:
    from .row import DataRow

_T = TypeVar("_T")


class SimpleData(Generic[_T]):
    def __init__(self, col_id: int):
        self.col_id = col_id

    def __get__(self, instance, owner) -> _T:
        return instance[self.col_id]


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
    def __init__(self, col_id: int, size: int, sep: int, el_type: Callable[[int], Generic[_T]]):
        self.accessors = []
        for i in range(size):
            self.accessors.append(el_type(col_id + i * sep))

    @classmethod
    def make(cls, size: int, sep: int, el_type: Callable[[int], Generic[_T]]) -> Callable[[int], 'ArrayData[_T]']:
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
