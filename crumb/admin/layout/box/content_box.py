from typing import TYPE_CHECKING

from flet import Control, Container, Stack, BoxShadow, ClipBehavior

from ..loader import Loader
from .box import Box
from .modal_box import ModalBox

if TYPE_CHECKING:
    from crumb.admin.app import CRuMbAdmin
    from crumb.admin.layout import Tab, PayloadInfo


__all__ = ["ContentsBoxContainer", "ContentBox"]


class ContentBox(Container, Box):
    def __init__(
            self,
            container: "ContentsBoxContainer",
            tab: "Tab",
    ):
        super().__init__(
            padding=10,
            clip_behavior=ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
            # чтобы растягивался на весь ContentBoxContainer
            top=0,
            right=0,
            left=0,
            bottom=0,
        )
        self.container = container
        self.tab = tab
        self.app = self.container.app
        self.resource = self.tab.resource
        self.on_close = self.tab.info.query.get('BOX_on_close')

        self._stack_controls: list[Control] = [Loader()]
        self.content = Stack(self._stack_controls)

    @property
    def payload(self):
        return self._stack_controls[0]

    @payload.setter
    def payload(self, v: Control):
        self._stack_controls[0] = v

    async def did_mount_async(self):
        await self.load_content()

    async def load_content(self, e=None):
        async with self.app.error_tracker():
            self.payload = await self.resource.get_payload(
                box=self,
                method=self.tab.info.method,
                **self.filter_payload_query(self.tab.info),
            )
            if hasattr(self.payload, '__tab_title__'):
                self.change_title(self.payload.__tab_title__)
                await self.tab.update_async()
            await self.update_async()

    async def reload_content(self, e=None):
        await self.load_content(e)

    def change_title(self, title: str):
        self.tab.title = title

    async def close(self):
        if self.on_close:
            self.on_close()
        await self.tab.close()

    async def add_modal(self, info: "PayloadInfo") -> ModalBox:
        modal = ModalBox(parent=self, info=info)
        self._stack_controls.append(modal)
        await self.update_async()
        return modal

    async def close_modal(self, modal: ModalBox) -> None:
        if modal is self.payload or modal not in self._stack_controls:
            return
        self._stack_controls.remove(modal)
        await self.update_async()


class ContentsBoxContainer(Container):

    def __init__(self, app: "CRuMbAdmin"):
        super().__init__(
            expand=True,
            bgcolor='white',
            shadow=BoxShadow(
                blur_radius=15,
                offset=(0, 15),
                color='#1C1B1F,0.2'
            ),
            clip_behavior=ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
        )
        self.app = app
        self.boxes = []
        self.content = Stack(self.boxes)

    def add_content_box(self, tab: "Tab") -> ContentBox:
        content_box = ContentBox(container=self, tab=tab)
        self.boxes.append(content_box)
        return content_box

    def rm_content_box(self, content: ContentBox):
        self.boxes.remove(content)
