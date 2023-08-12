from typing import Type

from tortoise import fields
from crumb.orm import fields as orm_fields

from .enums import FieldTypes


field_instance_to_type: dict[Type[fields.Field], FieldTypes] = {
    orm_fields.IntField:               FieldTypes.INT,
    orm_fields.SmallIntField:          FieldTypes.INT,
    orm_fields.BigIntField:            FieldTypes.INT,
    orm_fields.FloatField:             FieldTypes.FLOAT,
    orm_fields.CharField:              FieldTypes.STR,
    orm_fields.TextField:              FieldTypes.TEXT,
    orm_fields.BooleanField:           FieldTypes.BOOL,
    orm_fields.CharEnumFieldInstance:  FieldTypes.ENUM,
    orm_fields.IntEnumFieldInstance:   FieldTypes.ENUM,
    orm_fields.DateField:              FieldTypes.DATE,
    orm_fields.DatetimeField:          FieldTypes.DATETIME,
}
