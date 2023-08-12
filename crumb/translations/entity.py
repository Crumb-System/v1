from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .interface import InterfaceTranslation


@dataclass
class EntityTranslation:
    name: str
    name_plural: str

    _list: str
    _choice: str
    _creation: str
    list_template: str = '{self.name_plural}: {self._list}'
    choice_template: str = '{self.name_plural}: {self._choice}'
    create_template: str = '{self.name}: {self._creation}'
    edit_template: str = '{self.name}: {instance}'

    fields: dict[str, str] = field(default_factory=dict)

    interface: "InterfaceTranslation" = field(init=False)

    def list(self, **kwargs):
        return self.list_template.format(self=self, **kwargs)

    def choice(self, **kwargs):
        return self.choice_template.format(self=self, **kwargs)

    def create(self, **kwargs):
        return self.create_template.format(self=self, **kwargs)

    def edit(self, **kwargs):
        return self.edit_template.format(self=self, **kwargs)

    def field(self, name: str) -> Optional[str]:
        res = self.fields.get(name)
        if res is None:
            return self.interface.common_fields.get(name)
        return res
