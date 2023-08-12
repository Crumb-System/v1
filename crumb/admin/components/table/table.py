from flet import Container, Row, Column, OptionalNumber, ScrollMode

from .table_header import TableHeader
from .table_body import TableBody
from .table_row import TableRow


class Table(Container):
    def __init__(
            self,
            header: TableHeader,
            body: TableBody,
    ):
        super().__init__()
        self.header = header
        self.header.set_table(self)
        self.body = body
        self.body.set_table(self)
        self.content = Row([Column([self.header, self.body], spacing=0)], scroll=ScrollMode.AUTO)

    async def update_column_width(self, index: int, width: OptionalNumber):
        self.header.cells[index].width = width
        for row in self.body.rows:
            row.cells[index].width = width
        self.body.update_width()
        await self.update_async()

    def add_row(self, table_row: TableRow, index: int = -1):
        self.body.add_row(table_row=table_row, index=index)

    def scroll_to_async(self, row: TableRow):
        return self.body.scroll_to_async(key=row.key, duration=0)
