from typing import TYPE_CHECKING, Optional

from flet import DragTarget, DragTargetAcceptEvent, Draggable, \
    Container, Stack, Row, Text, TextSpan, \
    ScrollMode, border, padding

from crumb.admin.components.buttons import CloseButton

if TYPE_CHECKING:
    from crumb.admin.app import CRuMbAdmin
    from crumb.admin.layout import PayloadInfo


class Tab(Draggable):
    def __init__(self, bar: "TabsBar", info: "PayloadInfo", has_close: bool = True):
        super().__init__(group='tab')

        self.bar = bar
        self.info = info
        self.app = self.bar.app
        self.resource = self.app.find_resource(self.info.entity)

        self._title = TextSpan()
        row = [
            Text(spans=[self._title], color='black')
        ]
        if has_close:
            row.append(CloseButton(on_click=self.handle_close))
        self.container = Container(
            padding=padding.only(left=10),
            border=border.symmetric(horizontal=border.BorderSide(1, 'black,0.2')),
            content=Row(row, spacing=0),
            on_click=self.handle_click
        )
        self.title = self.resource.name_plural

        self.content = DragTarget(
            group='tab',
            content=self.container,
            on_accept=self.on_drag_accept
        )

        self.content_box = self.app.content_box_container.add_content_box(tab=self)

    @property
    def title(self) -> str:
        return self._title.text

    @title.setter
    def title(self, v: str):
        self._title.text = v

    @property
    def index(self):
        return self.bar.tab_index(self)

    async def handle_click(self, e):
        if self is not self.bar.selected:
            await self.bar.set_current_tab(self)

    async def handle_close(self, e):
        await self.close()

    async def close(self):
        await self.bar.rm_tab(self)

    def before_remove(self):
        self.app.content_box_container.rm_content_box(self.content_box)

    def activate(self):
        self.content_box.visible = True
        self.container.bgcolor = 'black,0.2'

    def deactivate(self):
        self.content_box.visible = False
        self.container.bgcolor = 'white'

    async def on_drag_accept(self, e: DragTargetAcceptEvent):
        tab: Tab = self.page.get_control(e.src_id)
        await self.bar.move_tab(tab.index, self.index)


class TabsBar(Container):
    _selected: Optional[Tab] = None

    def __init__(self, app: "CRuMbAdmin"):
        super().__init__(
            bgcolor='white',
            border=border.only(bottom=border.BorderSide(1, 'black,0.5')),
        )
        self.app = app
        self.tabs = []
        # первый row для того, чтобы контейнер заполнился на всю ширину контейнер, а второй для самих вкладок
        self.content = Stack([Row(), Row(
            controls=self.tabs,
            height=30,
            scroll=ScrollMode.ADAPTIVE,
            spacing=0,
        )])

    @property
    def selected(self) -> Optional[Tab]:
        return self._selected

    @selected.setter
    def selected(self, v: Optional[Tab]):
        assert v in self.tabs
        if self.selected is not None:
            self.selected.deactivate()
        self._selected = v
        if self.selected is not None:
            self.selected.activate()

    @property
    def selected_index(self) -> Optional[int]:
        if self.selected is None:
            return
        return self.tabs.index(self.selected)

    def tab_index(self, tab: Tab) -> int:
        return self.tabs.index(tab)

    def tab_by_info(self, info: "PayloadInfo") -> Optional[Tab]:
        resource = self.app.find_resource(info.entity)
        for i, tab in enumerate(self.tabs):
            if (
                    tab.info.entity == info.entity
                    and tab.info.method == info.method
                    and resource.compare_tab(tab.info.method, tab.info.query, info.query)
            ):
                return tab
        return None

    async def set_current_tab(self, tab: Tab):
        self.selected = tab
        await self.app.update_async()

    async def rm_tab(self, tab: Tab):
        if tab is self.selected:
            self.selected = self.tabs[tab.index - 1]
        tab.before_remove()
        self.tabs.remove(tab)
        await self.app.update_async()

    async def create_tab(self, info: "PayloadInfo"):
        tab = Tab(bar=self, info=info)
        self.tabs.append(tab)
        await self.set_current_tab(tab)

    async def move_tab(self, idx_from: int, idx_to: int):
        if idx_from == idx_to:
            return
        tab = self.tabs.pop(idx_from)
        self.tabs.insert(idx_to, tab)
        await self.update_async()
