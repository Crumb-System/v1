from typing import TypeVar, Generic, Self

from tortoise.queryset import QuerySet


T = TypeVar('T')


class Filter(Generic[T]):

    field: str
    value: T

    def __init__(self, field: str):
        self.field = field

    def __call__(self, value: T):
        new_instance = self.copy()
        new_instance.set_value(value)
        return new_instance

    def filter(self, query: QuerySet) -> QuerySet:
        raise NotImplementedError()

    def copy(self) -> Self:
        return self.__class__(self.field)

    def set_value(self, value) -> None:
        self.value = value
