from typing import TYPE_CHECKING

from flet import ListTile, Text, Icon, icons, TextOverflow

if TYPE_CHECKING:
    from .sidebar import Sidebar


class BtnPin(ListTile):
    def __init__(self, pinned: bool, sidebar: "Sidebar"):
        super().__init__(
            on_click=self.click_handler,
            on_long_press=self.long_click_handler
        )
        self.leading = Icon(size=24)
        self.title = Text(overflow=TextOverflow.CLIP, no_wrap=True, size=14)
        self.pinned = pinned
        self.sidebar = sidebar

    async def click_handler(self, e):
        if self.sidebar.expanded:
            self.sidebar.expanded = False
        self.pinned = not self.pinned
        await self.sidebar.update_async()

    async def long_click_handler(self, e):
        self.sidebar.expanded = True
        self.pinned = True
        self.selected = True
        await self.sidebar.update_async()

    @property
    def pinned(self):
        return self._pinned

    @pinned.setter
    def pinned(self, v: bool):
        self._pinned = v
        self.selected = v
        if self.pinned:
            self.leading.name = icons.CIRCLE_OUTLINED
            self.title.value = 'Открепить'
        else:
            self.leading.name = icons.PUSH_PIN_OUTLINED
            self.title.value = 'Закрепить'

    def minimize(self):
        self.title.visible = False

    def maximize(self):
        self.title.visible = True
