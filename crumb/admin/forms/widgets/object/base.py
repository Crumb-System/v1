from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypeVar, Generic, Type

from crumb.orm import BaseModel
from ..user_input import UserInputWidget, UserInput
from ... import InputGroup
from ...widget_containers import BaseWidgetContainer

if TYPE_CHECKING:
    from crumb.admin.resources import Resource


C = TypeVar('C', bound=BaseWidgetContainer)


class ObjectBaseWidget(Generic[C], UserInputWidget[dict[str, Any]]):
    child_container: Type[C]

    @property
    def final_value(self) -> dict[str, Any]:
        result = {}
        for field_name, widget in self.fields_map.items():
            if widget.ignore:
                continue
            value = widget.final_value
            if value is None and widget.ignore_if_none:
                continue
            result[field_name] = value
        return result

    def __init__(
            self,
            fields: list[UserInput | InputGroup],
            resource: "Resource" = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.fields = fields
        self.resource = resource
        self.fields_map: dict[str, UserInputWidget] = {}
        self.editable = False

    def _create_widget_in_container(self, item: UserInput) -> C:
        widget = item.widget(parent=self)
        self.fields_map[item.name] = widget
        return self.child_container(widget)

    def set_value_from_dict(self, data: dict[str, Any], initial: bool = False):
        for name, value in data.items():
            self.fields_map[name].set_value(value, initial=initial)

    def set_value_from_instance(self, instance: BaseModel, initial: bool = False):
        for f in self.fields:
            self.fields_map[f.name].set_value(
                self.resource.repository.get_instance_value(instance=instance, name=f.name),
                initial=initial
            )

    def set_value(self, value: dict[str, Any] | BaseModel, initial: bool = False):
        if initial and isinstance(value, BaseModel):
            assert self.resource is not None, f'{self.full_name} не имеет ресурса, но {value} - orm модель'
            assert self.resource.repository.model is value.__class__
            self.set_value_from_instance(value, initial=initial)
        else:
            assert isinstance(value, dict) and all(n in self.fields_map for n in value)
            self.set_value_from_dict(value, initial=initial)

    def is_valid(self) -> bool:
        valid = True
        for widget in self.fields_map.values():
            if not widget.is_valid():
                valid = False
        return valid

    def set_error(self, err: dict[str, Any]):
        if '__root__' in err:
            root = err.pop('__root__')
            # TODO: Как-то отображать root_errors
        for name, e in err.items():
            self.fields_map[name].set_error(e)


_OI = TypeVar('_OI', bound=ObjectBaseWidget)


@dataclass
class ObjectBase(UserInput[_OI]):
    fields: list[UserInput] = field(default_factory=list)
    resource: "Resource" = None
    default: dict[str, Any] = field(default_factory=dict)

    def add_field(self, item: UserInput | InputGroup) -> None:
        self.fields.append(item)
