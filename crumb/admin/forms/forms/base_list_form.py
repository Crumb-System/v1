from typing import TYPE_CHECKING

from flet import Row, TapEvent

from crumb.orm import BaseModel
from crumb.admin.components.table import Table, TableHeader, TableHeaderCell, TableBody, TableRow, TableCell
from . import Form
from .. import Primitive, WidgetSchemaCreator
from ..widgets import UserInput

if TYPE_CHECKING:
    from crumb.admin.layout import BOX


class BaseListForm(Form):
    body: Table
    table: Table  # alias body

    def __init__(
            self,
            box: "BOX",
            primitive: Primitive,
            request_limit: int = None,
            select_related: tuple[str] = None,
            prefetch_related: tuple[str] = None,
    ):
        super().__init__(box=box)
        self.app = self.box.app
        self.resource = self.box.resource
        widget_creator = WidgetSchemaCreator(resource=self.resource, all_read_only=True, allow_groups=False)
        self.widget_schemas: list[UserInput] = [widget_creator.from_primitive_item(item) for item in primitive]
        assert len(self.widget_schemas) > 0
        self.rows: list[TableRow] = []
        self.items: list[BaseModel] = []
        self.request_limit = request_limit
        self.current_total = 0
        self.has_next = True
        self.select_related = select_related
        self.prefetch_related = prefetch_related

    async def did_mount_async(self):
        await self.get_next_items()
        await self.update_async()

    def build_body(self) -> Table:
        self.table = Table(
            header=TableHeader(
                cells=[
                    TableHeaderCell(label=col.label, width=col.width)
                    for col in self.widget_schemas
                ]
            ),
            body=TableBody(
                rows=self.rows,
            )
        )
        return self.table

    def get_action_bar(self) -> Row:
        return Row([])

    async def get_next_items(self):
        new_items, total_count = await self.resource.repository(
            select_related=self.select_related,
            prefetch_related=self.prefetch_related,
        ).get_all(
            skip=self.current_total,
            limit=self.request_limit,
            sort=[],
            filters=[],
        )
        self.current_total += len(new_items)
        self.has_next = total_count != self.current_total
        self.items.extend(new_items)
        for item in new_items:
            self.add_row(item)

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
