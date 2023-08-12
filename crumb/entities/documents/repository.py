from typing import TypeVar

from tortoise.transactions import in_transaction

from crumb.repository import Repository, ValuesListRepository
from .model import Document, DocumentListValue


__all__ = ["DocumentRepository"]

from ...enums import FieldTypes

D = TypeVar('D', bound=Document)
DL = TypeVar('DL', bound=DocumentListValue)


class DocumentRepository(Repository[D]):

    hidden_fields = {'conducted'}
    calculated = {'unique_number': FieldTypes.STR}

    def can_edit(self):
        super().can_edit()
        if self.instance.conducted:
            raise Exception('Сначала нужно отменить проведение')

    def can_delete(self):
        super().can_edit()
        if self.instance.conducted:
            raise Exception('Сначала нужно отменить проведение')

    async def conduct(self):
        if self.instance.conducted:
            return
        async with in_transaction():
            await self.apply_side_effects()
            self.instance.conducted = True
            await self.instance.save(force_update=True, update_fields=('conducted',))

    async def unconduct(self):
        if not self.instance.conducted:
            return
        async with in_transaction():
            await self.cancel_side_effects()
            self.instance.conducted = False
            await self.instance.save(force_update=True, update_fields=('conducted', ))

    async def apply_side_effects(self):
        pass

    async def cancel_side_effects(self):
        pass
