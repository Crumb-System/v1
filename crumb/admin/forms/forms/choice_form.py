from typing import TYPE_CHECKING, Callable, Optional, Coroutine

from flet import Row, IconButton, icons, TapEvent

from crumb.constants import EMPTY_TUPLE
from crumb.orm import BaseModel
from crumb.admin.layout import PayloadInfo
from .base_list_form import BaseListForm

if TYPE_CHECKING:
    from crumb.admin.layout import BOX
    from .. import ModelInputForm, Primitive


class ChoiceForm(BaseListForm):

    def __init__(
            self,
            box: "BOX",
            primitive: "Primitive",
            make_choice: Callable[[Optional[BaseModel]], Coroutine[..., ..., None]],
            per_page: int = 25,
            per_page_variants: tuple[int, ...] = (10, 25, 50, 100),
            select_related: tuple[str] = EMPTY_TUPLE,
            prefetch_related: tuple[str] = EMPTY_TUPLE,
    ):
        super().__init__(
            box=box,
            primitive=primitive,
            per_page=per_page,
            per_page_variants=per_page_variants,
            select_related=select_related,
            prefetch_related=prefetch_related,
        )
        self.make_choice = make_choice

    async def on_double_click(self, e: TapEvent):
        await self.on_confirm(e)

    def get_action_bar(self) -> Row:
        buttons = [
            IconButton(icons.CHECK_CIRCLE_OUTLINE_ROUNDED, on_click=self.on_confirm, tooltip='Выбрать'),
            IconButton(icons.CLEANING_SERVICES_ROUNDED, on_click=self.on_clean, tooltip='Очистить'),
        ]
        if 'create' in self.resource.methods:
            buttons.append(
                IconButton(icons.ADD_CIRCLE_OUTLINE_ROUNDED, on_click=self.on_click_create, tooltip='Создать'),
            )
        return Row(buttons)

    async def on_confirm(self, e=None):
        async with self.app.error_tracker():
            active_row = self.table.active_row
            if active_row:
                await self.make_choice(active_row.instance)
                await self.close()

    async def on_clean(self, e=None):
        async with self.app.error_tracker():
            await self.make_choice(None)
            await self.close()

    async def on_click_create(self, e=None):
        async with self.app.error_tracker():
            await self.box.add_modal(PayloadInfo(
                entity=self.resource.entity(),
                method='create',
                query={'on_success': self.make_choice_on_create}
            ))

    async def make_choice_on_create(self, form: "ModelInputForm", instance: BaseModel):
        async with self.app.error_tracker():
            await self.make_choice(instance)
            await form.box.close()
            await self.close()
