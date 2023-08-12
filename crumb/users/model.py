from datetime import datetime
from typing import Optional

from crumb.entities.directories import Directory
from crumb.orm import fields as orm_fields


class BaseUser(Directory):
    id: int = orm_fields.BigIntField(pk=True)
    username: Optional[str] = orm_fields.CharField(max_length=40, null=True)

    password_hash: str = orm_fields.CharField(max_length=100)
    password_change_dt: datetime = orm_fields.DatetimeField()

    is_superuser: bool = orm_fields.BooleanField(default=False)
    can_login_admin: bool = orm_fields.BooleanField(default=False)
    is_active: bool = orm_fields.BooleanField(default=True)
    created_at: datetime = orm_fields.DatetimeField(auto_now_add=True)

    IEXACT_FIELDS = ('username',)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.username
