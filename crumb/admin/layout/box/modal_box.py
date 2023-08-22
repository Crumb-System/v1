from typing import TYPE_CHECKING

from flet import Container, Control, Row, Column, Text, MainAxisAlignment, ClipBehavior, Theme, ColorScheme

from .box import Box
from ..loader import Loader
from ...components.buttons import CloseButton

if TYPE_CHECKING:
    from .content_box import ContentBox
    from ..payload import PayloadInfo


class ModalBox(Container, Box):
    def __init__(
            self,
            parent: "ContentBox",
            info: "PayloadInfo",
    ):
        Container.__init__(
            self,
            top=0,
            bottom=0,
            left=0,
            right=0,
            padding=50,
            theme=Theme(color_scheme=ColorScheme(background='#f0f4fa'))
        )
        self.parent = parent
        self.info = info
        self.app = self.parent.app
        self.resource = self.app.find_resource(info.entity)
        self.on_close = self.info.query.get('BOX_on_close')

        # header
        self.box_title = Text(size=14)
        self.close_btn = CloseButton(on_click=self.handle_close, size=40)
        self.header = Row(
            controls=[self.box_title, self.close_btn],
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )

        # main_content
        self.payload_container = Column([self.header, Loader()])
        self.content = Container(
            content=self.payload_container,
            padding=10,
            clip_behavior=ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
            bgcolor='background',
            border_radius=12
        )

    @property
    def payload(self):
        return self.payload_container.controls[1]

    @payload.setter
    def payload(self, v: Control):
        self.payload_container.controls[1] = v

    async def did_mount_async(self):
        await self.load_content()

    async def load_content(self):
        async with self.app.error_tracker():
            self.payload = await self.resource.get_payload(
                box=self,
                method=self.info.method,
                **self.filter_payload_query(self.info),
            )
            if hasattr(self.payload, '__tab_title__'):
                self.change_title(self.payload.__tab_title__)
            await self.update_async()

    async def reload_content(self):
        await self.load_content()

    def change_title(self, title: str):
        self.box_title.value = title

    async def add_modal(self, info: "PayloadInfo") -> "ModalBox":
        return await self.parent.add_modal(info=info)

    async def close(self):
        if self.on_close:
            await self.on_close()
        await self.parent.close_modal(self)

    async def handle_close(self, e):
        await self.close()
