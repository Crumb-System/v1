from datetime import datetime

from crumb.orm import BaseModel, fields as orm_fields
from crumb.constants import REGISTRATOR_UNIQUE_NUMBER_MAX_LEN


__all__ = ["BaseRegister", "BaseRegisterResult"]


class BaseRegister(BaseModel):
    id: int = orm_fields.BigIntField(pk=True)
    registrator: str = orm_fields.CharField(max_length=REGISTRATOR_UNIQUE_NUMBER_MAX_LEN)
    dt: datetime = orm_fields.DatetimeField()

    class Meta:
        abstract = True


class BaseRegisterResult(BaseModel):
    id: str = orm_fields.CharField(pk=True, max_length=25, generated=False)
    dt: datetime = orm_fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
