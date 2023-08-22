from typing import TYPE_CHECKING, Any

from flet import Control, Column, Row, ScrollMode

from crumb.constants import UndefinedValue
from crumb.exceptions import ObjectErrors
from crumb.admin.forms.forms.form import Form
from crumb.admin.forms.schema import FormSchema, InputGroup
from crumb.admin.forms.widgets import UserInputWidget, UserInput
from crumb.admin.forms.widget_containers import SimpleWidgetContainer, BaseWidgetContainer

if TYPE_CHECKING:
    from crumb.admin.layout import BOX


FIELDS_MAP = dict[str, UserInputWidget]


class SimpleInputForm(Form):

    schema: FormSchema = None
    fields_map: FIELDS_MAP
    body: Column

    def __init__(
            self,
            box: "BOX",
            *,
            initial: dict[str, Any] = None
    ):
        super().__init__(box=box)
        self.fields_map = {}
        self.initial = initial

    def build_body(self):
        return Column(controls=self.build_inputs(), scroll=ScrollMode.AUTO)

    def build_inputs(self) -> list[Row | Column]:
        return [self._build_item(item=item) for item in self.get_form_schema()]

    def _build_item(self, item: UserInput | InputGroup) -> Row | Column | BaseWidgetContainer:
        if isinstance(item, UserInput):
            return self._create_widget_in_container(item)
        controls: list[Control] = []
        item: InputGroup
        for subgroup_or_input in item:
            if isinstance(subgroup_or_input, InputGroup):
                controls.append(self._build_item(subgroup_or_input))
            elif isinstance(subgroup_or_input, UserInput):
                controls.append(self._create_widget_in_container(subgroup_or_input))
            else:
                raise ValueError('что-то пошло не так')
        return item.to_control(controls)

    def _create_widget_in_container(self, item: UserInput):
        widget = item.widget(parent=self, initial=self.initial_for(item.name))
        self.fields_map[item.name] = widget
        return SimpleWidgetContainer(widget)

    def get_action_bar(self) -> Row:
        return Row(controls=[])

    def get_form_schema(self) -> FormSchema:
        assert self.schema
        return self.schema

    def set_object_errors(self, err: ObjectErrors):
        _err = err.to_error()
        if '__root__' in _err:
            root = _err.pop('__root__')
            # TODO: как-то отображать root_errors
        for field, e in _err.items():
            self.fields_map[field].set_error(e)

    def form_is_valid(self):
        is_valid = True
        for widget in self.fields_map.values():
            if not widget.is_valid():
                is_valid = False
        return is_valid

    @property
    def dirty_data(self):
        result = {}
        for name, widget in self.fields_map.items():
            if widget.ignore:
                continue
            value = widget.final_value
            if value is None and widget.ignore_if_none:
                continue
            result[name] = value
        return result

    def cleaned_data(self):
        return self.dirty_data

    def initial_for(self, name: str):
        if self.initial:
            return self.initial.get(name, UndefinedValue)
        return UndefinedValue

    def set_values(self, data: dict[str, Any]):
        for name, value in data.items():
            self.fields_map[name].set_value(value)

    def handle_value_change(self, widget: UserInputWidget):
        pass
