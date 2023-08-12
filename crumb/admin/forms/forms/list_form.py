from flet import Row, IconButton, icons, TapEvent

from crumb.admin.layout import PayloadInfo
from .base_list_form import BaseListForm, ListRecordRow


class ListForm(BaseListForm):
    async def on_double_click(self, e: TapEvent):
        row: ListRecordRow = e.control.row
        await self.app.open(PayloadInfo(
            entity=self.resource.entity(),
            method='edit',
            query={
                'pk': row.instance.pk
            }
        ))

    def get_action_bar(self) -> Row:
        return Row([
            IconButton(icons.ADD_CIRCLE_OUTLINE_ROUNDED, on_click=self.open_create_form, tooltip='Создать'),
            IconButton(icons.REPLAY_OUTLINED, on_click=self.box.reload_content, tooltip='Обновить'),
        ])

    async def open_create_form(self, e=None):
        await self.app.open(PayloadInfo(
            entity=self.resource.entity(),
            method='create',
        ))
