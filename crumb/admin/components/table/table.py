from typing import Generic, Optional

from flet import Container, Row, Column, OptionalNumber, ScrollMode

from .table_header import TableHeader
from .table_body import TableBody, TR


class Table(Generic[TR], Container):
    def __init__(
            self,
            header: TableHeader,
            body: TableBody[TR],
    ):
        super().__init__(expand=True)
        self.header = header
        self.header.set_table(self)
        self.body = body
        self.body.set_table(self)
        self.content = Row(
            [Column([self.header, self.body], spacing=0, expand=True)],
            scroll=ScrollMode.AUTO,
        )

    async def update_column_width(self, index: int, width: OptionalNumber):
        self.header.cells[index].width = width
        for row in self.body.rows:
            row.cells[index].width = width
        self.body.update_width()
        await self.update_async()

    def add_row(self, table_row: TR, index: int = -1):
        return self.body.add_row(table_row=table_row, index=index)

    def remove_row(self, index_or_row: int | TR):
        self.body.remove_row(index_or_row)

    def remove_all_rows(self):
        self.body.remove_all_rows()

    def get_row(self, index: int):
        return self.body.get_row(index)

    def swap_rows(self, r1: TR, r2: TR):
        self.body.swap_rows(r1, r2)

    @property
    def active_row(self):
        return self.body.active_row

    @active_row.setter
    def active_row(self, v: Optional[TR]):
        self.body.active_row = v

    @property
    def scroll_to_async(self):
        return self.body.scroll_to_async

    @property
    def length(self):
        return self.body.length

    def __iter__(self):
        return self.body.__iter__()

    def __getitem__(self, item):
        return self.body.rows.__getitem__(item)
