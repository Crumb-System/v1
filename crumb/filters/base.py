from typing import TypeVar, Generic, Self, Type, Iterable, Callable

from tortoise.queryset import QuerySet

from crumb.types import MODEL
from crumb.constants import UndefinedValue

__all__ = ["Filter", "EqualFilter", "InFilter", "LessFilter", "MoreFilter", "T"]

T = TypeVar('T')


class Filter(Generic[T]):
    value_factory: Callable[[], T] = None

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

    @property
    def value(self):
        if self.value_factory:
            return self.value_factory()
        return self._value

    @value.setter
    def value(self, v: T):
        self._value = v

    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        self._value_checks()
        return self._filter(query)

    def _value_checks(self):
        if self.value_factory is None:
            assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'

    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        raise NotImplementedError()


class EqualFilter(Filter[T]):
    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        return query.filter(**{self.field: self.value})


class LessMoreFilterBase(Filter[T]):
    def __init__(self, *args, equal: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.equal = equal

    def copy(self) -> Self:
        return self.__class__(
            model=self.model,
            field=self.field,
            equal=self.equal,
        )


class LessFilter(LessMoreFilterBase[T]):
    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        return query.filter(**{self.field + ('__lte' if self.equal else '__lt'): self.value})


class MoreFilter(LessMoreFilterBase[T]):
    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        return query.filter(**{self.field + ('__gte' if self.equal else '__gt'): self.value})


class InFilter(Filter[Iterable[T]]):
    def _value_checks(self):
        super()._value_checks()
        assert isinstance(self.value, Iterable), f'{self.__name__}, {self.model.__name__}, {self.field}'

    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        return query.filter(**{self.field + '__in': self.value})
