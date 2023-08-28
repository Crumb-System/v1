from typing import TypeVar, Generic, Self, Type, Iterable

from tortoise.queryset import QuerySet

from crumb.types import MODEL
from crumb.constants import UndefinedValue

__all__ = ["Filter", "EqualFilter", "InFilter", "T"]

T = TypeVar('T')


class Filter(Generic[T]):

    def __init__(self, model: Type[MODEL], field: str, value: T = UndefinedValue):
        self.model = model
        self.field = field
        self.value: T = value

    def __call__(self, value: T) -> Self:
        new_instance = self.copy()
        new_instance.value = value
        return new_instance

    def copy(self) -> Self:
        return self.__class__(
            model=self.model,
            field=self.field,
        )

    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        self._value_checks()
        return self._filter(query)

    def _value_checks(self):
        assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'

    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        raise NotImplementedError()


class EqualFilter(Filter[T]):
    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        return query.filter(**{self.field: self.value})


class InFilter(Filter[T]):

    def _value_checks(self):
        super()._value_checks()
        assert isinstance(self.value, Iterable), f'{self.__name__}, {self.model.__name__}, {self.field}'

    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        return query.filter(**{self.field + '__in': self.value})
