from typing import TYPE_CHECKING, Sequence

from flet import Row, TapEvent, Column

from crumb.constants import EMPTY_TUPLE
from crumb.orm import BaseModel
from crumb.admin.components.table import Table, TableHeader, TableHeaderCell, TableBody, TableRow, TableCell, Paginator
from . import Form
from .. import Primitive, WidgetSchemaCreator
from ..widgets import UserInput

if TYPE_CHECKING:
    from crumb.admin.layout import BOX


class BaseListForm(Form):
    body: Column

    def __init__(
            self,
            box: "BOX",
            primitive: Primitive,
            per_page: int = 25,
            per_page_variants: tuple[int, ...] = (10, 25, 50, 100),
            select_related: tuple[str] = EMPTY_TUPLE,
            prefetch_related: tuple[str] = EMPTY_TUPLE,
            sort: Sequence[str] = EMPTY_TUPLE
    ):
        super().__init__(box=box)
        self.app = self.box.app
        self.resource = self.box.resource
        widget_creator = WidgetSchemaCreator(resource=self.resource, all_read_only=True, allow_groups=False)
        self.widget_schemas: list[UserInput] = [widget_creator.from_primitive_item(item) for item in primitive]
        assert len(self.widget_schemas) > 0
        self.current_total = 0
        self.has_next = True
        self.select_related = select_related
        self.prefetch_related = prefetch_related

        self.table: Table[ListRecordRow] = Table(
            header=TableHeader(cells=[
                TableHeaderCell(label=col.label, width=col.width)
                for col in self.widget_schemas
            ]),
            body=TableBody()
        )
        self.paginator = Paginator(
            on_current_change=self.update_items,
            per_page=per_page,
            per_page_variants=per_page_variants,
        )
        self.sort = [sort] if isinstance(sort, str) else (EMPTY_TUPLE if sort is None else sort)

    async def did_mount_async(self):
        await self.update_items()

    def build_body(self):
        return Column([self.table, self.paginator])

    def get_action_bar(self) -> Row:
        return Row([])

    async def update_items(self):
        items, total = await self.resource.repository(
            select_related=self.select_related,
            prefetch_related=self.prefetch_related,
        ).get_all(
            skip=self.paginator.skip,
            limit=self.paginator.limit,
            sort=self.sort,
            filters=[]
        )
        self.paginator.total = total // self.paginator.per_page + 1
        self.paginator.build_pages()
        self.table.remove_all_rows()
        for item in items:
            self.add_row(item)
        await self.update_async()

    def add_row(self, instance: BaseModel):
        self.table.add_row(ListRecordRow(
            instance=instance,
            cells=[
                TableCell(
                    schema.widget(parent=self, initial=self.initial_for(instance, schema.name)),
                    on_double_click=self.on_double_click
                )
                for schema in self.widget_schemas
            ]
        ))

    async def on_double_click(self, e: TapEvent):
        pass

    def initial_for(self, item: BaseModel, field_name: str):
        return self.resource.repository.get_instance_value(item, field_name)

    async def close(self):
        await self.box.close()


class ListRecordRow(TableRow):
    def __init__(
            self,
            instance: BaseModel,
            cells: list[TableCell] = None,
    ):
        super().__init__(cells=cells)
        self.instance = instance
