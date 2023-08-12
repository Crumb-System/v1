from typing import TYPE_CHECKING, Callable, Coroutine

from flet import Row, Column, Text, Container, Control, MainAxisAlignment, ClipBehavior, alignment

from crumb.admin.components.buttons import CloseButton

if TYPE_CHECKING:
    from crumb.admin.app import CRuMbAdmin


class Popup(Container):
    def __init__(
            self,
            app: "CRuMbAdmin",
            content: Control,
            title: str = None,
            on_close: Callable[[], Coroutine[..., ..., None]] = None,
            size: tuple[float | int, float | int] = None
    ):
        super().__init__(
            top=0,
            left=0,
            right=0,
            bottom=0,
            bgcolor='grey,0.1',
            blur=5,
            alignment=alignment.center,
        )
        self.app = app
        self.on_close = on_close

        self.__title__ = Text()
        self.set_title(title)
        self._header = Row(
            controls=[self.__title__, CloseButton(on_click=self.close)],
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )
        self.column = Column(
            controls=[
                self._header,
                content
            ]
        )
        self.content = self.container = Container(
            content=self.column,
            clip_behavior=ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
            bgcolor='#ececec',
            padding=10,
            border_radius=15,
        )
        if size:
            self.set_size(*size)

    async def close(self, e=None):
        if self.on_close:
            await self.on_close()
        await self.app.close_popup(self)

    def set_title(self, text: str):
        self.__title__.value = text

    def set_size(self, width: int | float = None, height: int | float = None):
        if width:
            self.container.width = width
        if height:
            self.container.height = height
