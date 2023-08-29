from dataclasses import dataclass, field
from typing import TypeVar, Any, TypedDict
from uuid import UUID

from tortoise import fields
from crumb.orm import fields as orm_fields

from crumb.orm.base_model import BaseModel, ListValueModel
from .enums import FieldTypes


MODEL = TypeVar('MODEL', bound=BaseModel)
LIST_VALUE_MODEL = TypeVar('LIST_VALUE_MODEL', bound=ListValueModel)
PK = TypeVar('PK', int, str, UUID)
DATA = dict[str, Any]
FK_TYPE = orm_fields.IntField | orm_fields.SmallIntField | orm_fields.BigIntField |\
          orm_fields.UUIDField | orm_fields.CharField | fields.Field


BackFKData = list[DATA]
ValuesListData = TypedDict('ValuesListData', fields={
    'head': tuple[str, ...],
    'values': list[tuple[Any, ...]]
})


@dataclass
class SortedData:
    db_field: dict[str, Any] = field(default_factory=dict)
    extra: DATA = field(default_factory=dict)
    o2o: dict[str, DATA] = field(default_factory=dict)
    o2o_pk: dict[str, int] = field(default_factory=dict)
    fk: dict[str, DATA] = field(default_factory=dict)
    fk_pk: dict[str, int] = field(default_factory=dict)
    back_o2o: dict[str, DATA] = field(default_factory=dict)
    back_fk: dict[str, BackFKData | ValuesListData] = field(default_factory=dict)


@dataclass
class RepositoryDescription:
    all: dict[str, FieldTypes] = field(default_factory=dict)
    db_field: dict[str, fields.Field] = field(default_factory=dict)
    o2o: dict[str, fields.relational.OneToOneFieldInstance] = field(default_factory=dict)
    o2o_pk: dict[str, FK_TYPE] = field(default_factory=dict)
    fk: dict[str, fields.relational.ForeignKeyFieldInstance] = field(default_factory=dict)
    fk_pk: dict[str, FK_TYPE] = field(default_factory=dict)
    back_o2o: dict[str, fields.relational.BackwardOneToOneRelation] = field(default_factory=dict)
    back_fk: dict[str, fields.relational.BackwardFKRelation] = field(default_factory=dict)
    hidden: dict[str, fields.Field] = field(default_factory=dict)
