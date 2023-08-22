from dataclasses import dataclass, field
from typing import Any

from flet import Container, Column, Row, IconButton, icons, ScrollMode

from crumb.constants import UndefinedValue
from crumb.orm import BaseModel
from crumb.admin.components.table import Table, TableHeader, TableHeaderCell, TableBody
from crumb.types import ValuesListData
from .object import ObjectTableRow, ObjectTableRowWidget
from .user_input import UserInput, UserInputWidget


class TableInputWidget(UserInputWidget[list[dict[str, Any]]], Container):

    @property
    def final_value(self) -> ValuesListData:
        result = {
            'head': (head := tuple(schema.name for schema in self.object_schema.fields)),
            'values': (values := []),
        }
        for widget in self.table:
            value = widget.final_value
            values.append(tuple(value.get(name, UndefinedValue) for name in head))
        return result

    def __init__(
            self,
            object_schema: ObjectTableRow,
            variant: str = 'table',
            rows_count: int = 11,
            **kwargs
    ):
        Container.__init__(self, padding=12)
        UserInputWidget.__init__(self, **kwargs)

        self.object_schema = object_schema
        self.variant = variant
        self.rows_count = rows_count

        self.actions = self.get_action_bar()
        self.table = self.create_table()
        self.content = Column([
            self.actions,
            self.table
        ])
        self.editable = False
        self.__finalize_init__()

    def get_action_bar(self):
        return Row([
            IconButton(
                icons.ADD_CIRCLE_OUTLINE_OUTLINED,
                on_click=self.handle_add_row,
                icon_color='green',
                tooltip='Добавить'
            ),
            IconButton(
                icons.REMOVE_CIRCLE_OUTLINE_OUTLINED,
                on_click=self.handle_delete_row,
                icon_color='error',
                tooltip='Удалить'
            ),
            IconButton(
                icons.ARROW_CIRCLE_UP_OUTLINED,
                on_click=self.handle_move_row_up,
                icon_color='primary',
                tooltip='Переместить вверх'
            ),
            IconButton(
                icons.ARROW_CIRCLE_DOWN_OUTLINED,
                on_click=self.handle_move_row_down,
                icon_color='primary',
                tooltip='Переместить вниз'
            ),
        ], scroll=ScrollMode.AUTO)

    def create_table(self) -> Table[ObjectTableRowWidget]:
        return Table(
            header=TableHeader(
                cells=[
                    TableHeaderCell(label=col.label, width=col.width)
                    for col in self.object_schema.fields
                ]
            ),
            body=TableBody(),
        )

    def create_table_row(self, initial: BaseModel | dict[str, Any] = UndefinedValue) -> ObjectTableRowWidget:
        widget = self.object_schema.widget(parent=self, initial=initial)
        self.table.add_row(widget)
        return widget

    async def handle_add_row(self, e):
        widget = self.create_table_row()
        widget.set_value({'ordering': self.table.body.length})
        self.table.active_row = widget
        await self.table.scroll_to_async(offset=-1, duration=10)

    async def handle_delete_row(self, e):
        active_row = self.table.active_row
        if active_row is None:
            return
        idx = active_row.index
        table_length = self.table.length
        if idx == 0:
            if table_length == 1:
                self.table.active_row = None
            else:
                self.table.active_row = self.table.get_row(1)
        elif idx == table_length - 1:
            self.table.active_row = self.table.get_row(idx - 1)
        else:
            self.table.active_row = self.table.get_row(idx + 1)
        self.table.remove_row(active_row)
        for i, row in enumerate(self.table[idx:], start=idx + 1):
            row.set_value({'ordering': i})
        await self.table.update_async()

    async def handle_move_row_up(self, e):
        active_row = self.table.active_row
        if active_row is None:
            return
        idx = active_row.index
        if idx == 0:
            return
        self.swap_rows(active_row, self.table.get_row(idx - 1))
        await self.table.body.update_async()

    async def handle_move_row_down(self, e):
        active_row = self.table.active_row
        if active_row is None:
            return
        idx = active_row.index
        if idx == self.table.length - 1:
            return
        self.swap_rows(active_row, self.table.get_row(idx + 1))
        await self.table.update_async()

    def swap_rows(self, r1: ObjectTableRowWidget, r2: ObjectTableRowWidget):
        self.table.swap_rows(r1, r2)
        r1.set_value({'ordering': r1.index + 1})
        r2.set_value({'ordering': r2.index + 1})

    def set_value(self, value: Any, initial: bool = False):
        if initial:
            assert all(isinstance(v, BaseModel) for v in value)
            for v in sorted(value, key=lambda x: x.ordering):
                self.create_table_row(initial=v)
            return
        assert isinstance(value, dict) and all(isinstance(k, int) for k in value)
        for index, row_value in value.items():
            self.table.get_row(index).set_value(row_value)

    def set_error(self, err: dict[int, dict[str, Any]]):
        for index, error in err.items():
            self.table.get_row(index).set_error(error)

    def is_valid(self) -> bool:
        valid = True
        for widget in self.table:
            if not widget.is_valid():
                valid = False
        return valid


@dataclass
class TableInput(UserInput[TableInputWidget]):
    object_schema: ObjectTableRow = None
    variant: str = 'table'
    width: int = None
    height: int = 400
    rows_count: int = 11
    default: list = field(default_factory=list)

    @property
    def widget_type(self):
        return TableInputWidget

    def add_field(self, item: UserInput) -> None:
        self.object_schema.fields.append(item)
