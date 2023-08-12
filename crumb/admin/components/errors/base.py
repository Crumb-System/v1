import json
from typing import TYPE_CHECKING, Generic, TypeVar

from flet import UserControl, Container, Column, Row, Text, ElevatedButton, icons, ScrollMode, ClipBehavior


if TYPE_CHECKING:
    from crumb.admin.app import CRuMbAdmin


E = TypeVar('E', bound=Exception)


class ErrorContainer(Generic[E], UserControl):
    default_title: str = ''

    def __init__(
            self,
            app: "CRuMbAdmin",
            error: E,
    ):
        UserControl.__init__(self)
        self.app = app
        self.error = error
        self.error_text = self.get_error_text()

    def get_error_text(self) -> Text:
        pass

    def build(self):
        return Column([
            Container(
                Column(
                    controls=[
                        Row(
                            controls=[self.error_text],
                            scroll=ScrollMode.AUTO,
                            width=1000
                        )
                    ],
                    scroll=ScrollMode.AUTO,
                    height=500
                ),
                clip_behavior=ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
                bgcolor='white',
            ),
            ElevatedButton(
                icon=icons.CONTENT_COPY_ROUNDED,
                text='Копировать в буфер',
                on_click=self.copy_error_to_clipboard
            )
        ])

    async def copy_error_to_clipboard(self, e=None):
        await self.app.page.set_clipboard_async(self.error_text.value)

    def get_default_title(self) -> str:
        return self.default_title

    @classmethod
    async def open_in_popup(cls, app: "CRuMbAdmin", error: E, title: str = None):
        self = cls(app=app, error=error)
        await app.add_popup(self, title=title or self.get_default_title(), size=(700, 610))
