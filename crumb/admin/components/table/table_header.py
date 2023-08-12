from typing import TYPE_CHECKING

from flet import Container, Row

from .table_header_cell import TableHeaderCell

if TYPE_CHECKING:
    from . import Table, TableBody


class TableHeader(Container):
    table: "Table"

    def __init__(
            self,
            cells: list[TableHeaderCell] = None,
    ):
        super().__init__(bgcolor='#DDDCDF')
        self.cells = cells or []
        self.content = Row(controls=self.cells, height=35, spacing=0)
        for cell in cells:
            cell.set_header(self)

    def add_cell(self, cell: TableHeaderCell, index: int = -1):
        assert index == -1 or index >= 1
        if index == -1:
            self.cells.append(cell)
        else:
            self.cells.insert(index, cell)
        cell.set_header(self)

    def set_table(self, table: "Table"):
        self.table = table

    @property
    def body(self) -> "TableBody":
        return self.table.body

    @property
    def length(self) -> int:
        return len(self.cells)
