from dataclasses import dataclass

from crumb.admin.components.table import TableRow
from .base import ObjectBase, ObjectBaseWidget
from ..user_input import UserInput
from ...widget_containers import TableCellWidgetContainer


class ObjectTableRowWidget(ObjectBaseWidget[TableCellWidgetContainer], TableRow):
    child_container = TableCellWidgetContainer

    @property
    def full_name(self) -> str:
        return f'{self.parent.full_name}.{self.index}'

    def __init__(self, **kwargs):
        ObjectBaseWidget.__init__(self, **kwargs)
        TableRow.__init__(self)
        assert all(isinstance(f, UserInput) for f in self.fields), "Можно устанавливать только виджеты, не группы"
        self.build_cells()
        self.__finalize_init__()

    def build_cells(self) -> None:
        for widget_container in self.get_controls():
            self.add_cell(widget_container)

    def get_controls(self) -> list[TableCellWidgetContainer]:
        return [self._create_widget_in_container(f) for f in self.fields]


@dataclass
class ObjectTableRow(ObjectBase[ObjectTableRowWidget]):

    @property
    def widget_type(self):
        return ObjectTableRowWidget
