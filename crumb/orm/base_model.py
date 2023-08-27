from typing import TYPE_CHECKING, Type
from typing_extensions import deprecated

from tortoise import Model, fields
from . import fields as orm_fields

if TYPE_CHECKING:
    from crumb.repository import REPOSITORY


__all__ = ["BaseModel", "ListValueModel"]


class BaseModel(Model):
    BASE_PERMISSIONS: tuple[str, ...] = ('get', 'create', 'edit', 'delete')
    EXTRA_PERMISSIONS: tuple[str, ...] = ()
    CASE_INSENSITIVE: tuple[str, ...] = ()

    REPOSITORIES: dict[str, Type["REPOSITORY"]]

    class Meta:
        abstract = True

    @property
    @deprecated('use CASE_INSENSITIVE instead, IEXACT_FIELDS will be removed in 1.1')
    def IEXACT_FIELDS(self):
        return self.CASE_INSENSITIVE

    @classmethod
    def is_case_insensitive(cls, field_name: str):
        return field_name in cls.CASE_INSENSITIVE


class ListValueModel(BaseModel):
    """Модель для строк табличной части"""
    id: str = orm_fields.CharField(pk=True, max_length=15, generated=False)
    owner: fields.ForeignKeyRelation
    ordering: int = orm_fields.SmallIntField(editable=False)

    def set_pk(self):
        self.pk = f'{self.owner.pk};{self.ordering}'

    class Meta:
        abstract = True
