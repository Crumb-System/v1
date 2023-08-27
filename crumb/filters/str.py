from typing import Self

from tortoise.queryset import QuerySet

from crumb.types import MODEL
from crumb.constants import UndefinedValue
from .base import Filter


__all__ = ["StrEqualFilter", "StrStartswithFilter", "StrEndswithFilter", "StrContainsFilter"]


class StrBaseFilter(Filter[str]):
    def __init__(self, *args, case_insensitive: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.case_insensitive = case_insensitive

    def copy(self) -> Self:
        return self.__class__(
            model=self.model,
            field=self.field,
            case_insensitive=self.case_insensitive
        )


class StrEqualFilter(StrBaseFilter):
    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'
        if self.model.is_case_insensitive(self.field):
            field_name = self.field + '__iexact'
        else:
            field_name = self.field
        return query.filter(**{field_name: self.value})


class StrStartswithFilter(StrBaseFilter):
    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'
        if self.model.is_case_insensitive(self.field):
            field_name = self.field + '__istartswith'
        else:
            field_name = self.field + '__startswith'
        return query.filter(**{field_name: self.value})


class StrEndswithFilter(StrBaseFilter):
    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'
        if self.model.is_case_insensitive(self.field):
            field_name = self.field + '__iendswith'
        else:
            field_name = self.field + '__endswith'
        return query.filter(**{field_name: self.value})


class StrContainsFilter(StrBaseFilter):
    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'
        if self.model.is_case_insensitive(self.field):
            field_name = self.field + '__icontains'
        else:
            field_name = self.field + '__contains'
        return query.filter(**{field_name: self.value})
