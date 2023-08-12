from typing import TYPE_CHECKING, Callable, Coroutine, Optional

from flet import Container, GestureDetector, Control, MouseCursor, alignment, padding, TapEvent

if TYPE_CHECKING:
    from . import Table, TableHeader, TableBody, TableRow


class TableCell(GestureDetector):
    row: "TableRow"

    def __init__(
            self,
            content: Control,
            on_click: Callable[[TapEvent], Coroutine[..., ..., None]] = None,
            on_double_click: Callable[[TapEvent], Coroutine[..., ..., None]] = None,
    ):
        GestureDetector.__init__(
            self,
            mouse_cursor=MouseCursor.CLICK,
            on_tap_down=self.click_handler,
        )
        self.on_click = on_click
        self.on_double_click = on_double_click
        self.content = self.container = Container(
            content=content,
            alignment=alignment.center_left,
            padding=padding.symmetric(horizontal=5)
        )

    def set_row(self, row: "TableRow"):
        self.row = row

    async def click_handler(self, e: TapEvent):
        self.activate_row()
        if self.on_click:
            await self.on_click(e)
        await self.body.update_async()

    async def double_click_handler(self, e: TapEvent):
        self.activate_row()
        await self.on_double_click(e)
        if self.body.page:  # если не удаляется:)
            await self.body.update_async()

    @property
    def on_double_click(self) -> Optional[Callable[[TapEvent], Coroutine[..., ..., None]]]:
        return self._on_double_click

    @on_double_click.setter
    def on_double_click(self, v: Optional[Callable[[TapEvent], Coroutine[..., ..., None]]]):
        self._on_double_click = v
        if self._on_double_click:
            self.on_double_tap_down = self.double_click_handler
        else:
            self.on_double_tap_down = None

    def activate_row(self):
        self.body.active_row = self.row

    @property
    def table(self) -> "Table":
        return self.row.body.table

    @property
    def header(self) -> "TableHeader":
        return self.row.body.table.header

    @property
    def body(self) -> "TableBody":
        return self.row.body

    def change_bgcolor(self):
        row = self.row
        if row.is_active:
            self.container.bgcolor = row.ACTIVE_BGCOLOR
        elif row.is_selected:
            self.container.bgcolor = row.SELECTED_BGCOLOR
        else:
            self.container.bgcolor = row.DEFAULT_BGCOLOR
