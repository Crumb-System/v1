from tortoise.queryset import QuerySet

from crumb.types import MODEL
from crumb.constants import UndefinedValue
from .base import Filter, EqualFilter


class StrEqualFilter(EqualFilter[str]):
    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'
        if self.model.is_case_insensitive(self.field):
            field_name = self.field + '__iexact'
        else:
            field_name = self.field
        return query.filter(**{field_name: self.value})


class StrStartswithFilter(Filter[str]):
    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'
        if self.model.is_case_insensitive(self.field):
            field_name = self.field + '__istartswith'
        else:
            field_name = self.field + '__startswith'
        return query.filter(**{field_name: self.value})


class StrEndswithFilter(Filter[str]):
    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'
        if self.model.is_case_insensitive(self.field):
            field_name = self.field + '__iendswith'
        else:
            field_name = self.field + '__endswith'
        return query.filter(**{field_name: self.value})


class StrContainsFilter(Filter[str]):
    def filter(self, query: QuerySet[MODEL]) -> QuerySet[MODEL]:
        assert self.value is not UndefinedValue, f'{self.__name__}, {self.model.__name__}, {self.field}'
        if self.model.is_case_insensitive(self.field):
            field_name = self.field + '__icontains'
        else:
            field_name = self.field + '__contains'
        return query.filter(**{field_name: self.value})
