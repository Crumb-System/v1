from typing import TYPE_CHECKING, Literal

from flet import GestureDetector, Container, MouseCursor, DragStartEvent, DragUpdateEvent

if TYPE_CHECKING:
    from crumb.admin.components.table import TableHeaderCell


class WidthChanger(GestureDetector):
    global_x_on_start: float
    width_on_start: float | int
    change_cell: "TableHeaderCell"

    def __init__(
            self,
            cell: "TableHeaderCell",
            side: Literal['left', 'right']
    ):
        super().__init__(
            content=Container(width=10),
            mouse_cursor=MouseCursor.RESIZE_COLUMN,
            top=0,
            bottom=0,
            drag_interval=100,
            on_horizontal_drag_start=self.handle_start,
            on_horizontal_drag_update=self.handle_update,
        )
        self.side = side
        if self.side == 'left':
            self.left = 0
        else:
            self.right = 0
        self.cell = cell

    def handle_start(self, e: DragStartEvent):
        if self.side == 'left':
            header = self.cell.header
            self.change_cell = header.cells[header.cells.index(self.cell) - 1]
        else:
            self.change_cell = self.cell
        self.global_x_on_start = e.global_x
        self.width_on_start = self.change_cell.width

    async def handle_update(self, e: DragUpdateEvent):
        new_width = self.width_on_start + (e.global_x - self.global_x_on_start)
        cell = self.change_cell
        await cell.table.update_column_width(
            index=cell.header.cells.index(cell),
            width=max((cell.MIN_WIDTH, new_width))
        )
