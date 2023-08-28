from typing import Self

from tortoise.queryset import QuerySet

from crumb.types import MODEL
from crumb.constants import UndefinedValue
from .base import Filter, InFilter


__all__ = ["StrEqualFilter", "StrInFilter", "StrStartswithFilter", "StrEndswithFilter", "StrContainsFilter"]


class StrBaseFilter(Filter[str]):
    def __init__(self, *args, case_insensitive: bool = UndefinedValue, **kwargs):
        super().__init__(*args, **kwargs)
        self._case_insensitive = case_insensitive

    def copy(self) -> Self:
        return self.__class__(
            model=self.model,
            field=self.field,
            case_insensitive=self._case_insensitive
        )

    @property
    def case_insensitive(self):
        if self._case_insensitive is UndefinedValue:
            return self.model.is_case_insensitive(self.field)
        return self._case_insensitive


class StrEqualFilter(StrBaseFilter):
    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        if self.case_insensitive:
            field_name = self.field + '__iexact'
        else:
            field_name = self.field
        return query.filter(**{field_name: self.value})


class StrInFilter(InFilter[str]):
    pass


class StrStartswithFilter(StrBaseFilter):
    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        if self.case_insensitive:
            field_name = self.field + '__istartswith'
        else:
            field_name = self.field + '__startswith'
        return query.filter(**{field_name: self.value})


class StrEndswithFilter(StrBaseFilter):
    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        if self.case_insensitive:
            field_name = self.field + '__iendswith'
        else:
            field_name = self.field + '__endswith'
        return query.filter(**{field_name: self.value})


class StrContainsFilter(StrBaseFilter):
    def _filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        if self.case_insensitive:
            field_name = self.field + '__icontains'
        else:
            field_name = self.field + '__contains'
        return query.filter(**{field_name: self.value})
