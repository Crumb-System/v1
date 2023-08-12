from typing import TYPE_CHECKING

from flet import (
    Container, Stack, Text,
    ClipBehavior, TextOverflow, padding, alignment,
)

from .width_changer import WidthChanger

if TYPE_CHECKING:
    from . import Table, TableHeader, TableBody


class TableHeaderCell(Container):
    header: "TableHeader"

    MIN_WIDTH = 12

    global_x_on_width_change_start: float
    width_on_width_change_start: float | int

    def __init__(
            self,
            label: str,
            width: int | float = 250,
    ):
        super().__init__(clip_behavior=ClipBehavior.ANTI_ALIAS)

        self.width = width
        self.real_content = Container(
            Text(label, overflow=TextOverflow.ELLIPSIS, size=15),
            padding=padding.symmetric(horizontal=5),
            clip_behavior=ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
            alignment=alignment.center_left
        )
        self.content = Stack([self.real_content, WidthChanger(self, side='left'), WidthChanger(self, side='right')])

    def set_header(self, header: "TableHeader"):
        self.header = header
        self.height = self.header.height

    @property
    def table(self) -> "Table":
        return self.header.table

    @property
    def body(self) -> "TableBody":
        return self.header.table.body
