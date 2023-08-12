from typing import TYPE_CHECKING, Optional

from flet import ListView as FletListView

from crumb.utils import default_if_none
from .table_row import TableRow

if TYPE_CHECKING:
    from . import Table, TableHeader


class TableBody(FletListView):
    table: "Table"
    rows: list[TableRow]
    row_height = 30

    _active_row: TableRow = None

    def __init__(
            self,
            rows: list[TableRow] = None,
            rows_count: int = None,
    ):
        super().__init__(
            item_extent=self.row_height,
            spacing=0,
        )
        if rows_count:
            self.height = self.row_height * rows_count
        self.rows = default_if_none(rows, [])
        self.controls = self.rows

    def set_table(self, table: "Table"):
        self.table = table

        header_length = self.header.length
        assert all(row.length == header_length for row in self.rows)
        for row in self.rows:
            row.set_body(self)
        for i, hc in enumerate(self.header.cells):
            w = hc.width
            for row in self.rows:
                row.cells[i].width = w
        self.update_width()

    def add_row(self, table_row: TableRow, index: int = -1):
        assert index == -1 or index >= 1
        assert table_row.length == self.header.length
        if index == -1:
            self.rows.append(table_row)
        else:
            self.rows.insert(index, table_row)
        for i, hc in enumerate(self.header.cells):
            table_row.cells[i].width = hc.width
        table_row.set_body(self)

    def update_width(self):
        self.width = sum([c.width for c in self.header.cells])

    @property
    def length(self) -> int:
        return len(self.rows)

    @property
    def header(self) -> "TableHeader":
        return self.table.header

    @property
    def active_row(self) -> Optional[TableRow]:
        return self._active_row

    @active_row.setter
    def active_row(self, v: Optional[TableRow]):
        if self._active_row and self._active_row is v:
            return
        prev = self._active_row
        self._active_row = v
        if prev:
            prev.deactivate()
        if self._active_row:
            self._active_row.activate()
