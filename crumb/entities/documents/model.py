from datetime import datetime

from crumb.orm import fields as orm_fields

from crumb.orm.base_model import BaseModel, ListValueModel


__all__ = ["Document", "DocumentListValue"]


class Document(BaseModel):
    """Базовый класс для всех документов"""

    PREFIX: str
    id: int = orm_fields.BigIntField(pk=True)
    conducted: bool = orm_fields.BooleanField(default=False)
    dt: datetime = orm_fields.DatetimeField(auto_now_add=True)
    comment: str = orm_fields.TextField()

    @property
    def unique_number(self):
        return f'{self.PREFIX}-{self.id}'

    class Meta:
        abstract = True


class DocumentListValue(ListValueModel):
    """Базовая модель списка для документов"""

    class Meta:
        abstract = True
