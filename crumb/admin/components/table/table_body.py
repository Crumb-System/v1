from typing import TYPE_CHECKING, Optional, Generic, TypeVar, Iterator

from flet import Container, ListView as FletListView, ClipBehavior

from crumb.utils import default_if_none
from .table_row import TableRow

if TYPE_CHECKING:
    from . import Table, TableHeader

TR = TypeVar('TR', bound=TableRow)


class TableBody(Generic[TR], Container):
    table: "Table[TR]"
    rows: list[TR]
    row_height = 30

    _active_row: TR = None

    def __init__(
            self,
            rows: list[TR] = None,
    ):
        super().__init__(clip_behavior=ClipBehavior.ANTI_ALIAS, expand=True)
        self.content = self.list = FletListView(item_extent=self.row_height, spacing=0)
        self.list.controls = default_if_none(rows, [])

    @property
    def rows(self):
        return self.list.controls

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

    def get_row(self, index: int) -> TR:
        return self.rows[index]

    def __iter__(self) -> Iterator[TR]:
        return self.rows.__iter__()

    def add_row(self, table_row: TR, index: int = -1):
        assert index == -1 or index >= 1
        assert table_row.length == self.header.length
        if index == -1:
            self.rows.append(table_row)
        else:
            self.rows.insert(index, table_row)
        for i, hc in enumerate(self.header.cells):
            table_row.cells[i].width = hc.width
        table_row.set_body(self)
        return table_row

    def remove_row(self, index_or_row: int | TR):
        if isinstance(index_or_row, int):
            self.rows.pop(index_or_row)
        else:
            self.rows.remove(index_or_row)

    def remove_all_rows(self):
        self.active_row = None
        self.rows.clear()

    def update_width(self):
        self.width = sum([c.width for c in self.header.cells])

    @property
    def length(self) -> int:
        return len(self.rows)

    @property
    def header(self) -> "TableHeader":
        return self.table.header

    @property
    def active_row(self) -> Optional[TR]:
        return self._active_row

    @active_row.setter
    def active_row(self, v: Optional[TR]):
        if self._active_row and self._active_row is v:
            return
        prev = self._active_row
        self._active_row = v
        if prev:
            prev.deactivate()
        if self._active_row:
            self._active_row.activate()

    def swap_rows(self, r1: TR, r2: TR):
        i1 = r1.index
        i2 = r2.index
        self.rows[i1], self.rows[i2] = r2, r1

    @property
    def scroll_to_async(self):
        return self.list.scroll_to_async
