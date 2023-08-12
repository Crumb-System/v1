from typing import Any

from . import widgets, InputGroup


PRIMITIVE_ITEM = tuple[str, dict[str, Any]] | dict[str, Any] | widgets.UserInput | InputGroup


class Primitive:
    def __init__(self, *items: str | PRIMITIVE_ITEM, allow_groups: bool = True):
        self.items: list[PRIMITIVE_ITEM] = []
        for v in items:
            self.add(v)

    def __iter__(self):
        return self.items.__iter__()

    def add(self, item: str | PRIMITIVE_ITEM, index: int = -1) -> "Primitive":
        item = (item, {}) if isinstance(item, str) else item
        if index == -1:
            self.items.append(item)
        else:
            self.items.insert(index, item)
        return self

    def get(self, name: str) -> PRIMITIVE_ITEM:
        for item in self.items:
            if self.is_schema(item):
                item_name = item.name
            elif self.is_group(item):
                item_name = item.get('name')
            else:
                item_name = item[0]
            if item_name == name:
                return item

    def has(self, name: str) -> bool:
        return self.get(name) is not None

    def remove(self, name: str) -> "Primitive":
        item = self.get(name)
        if item:
            self.items.remove(item)
        return self

    def copy(self):
        return Primitive(*self.items)

    @staticmethod
    def is_field_with_extra(item: PRIMITIVE_ITEM) -> bool:
        return (
                isinstance(item, tuple)
                and len(item) == 2
                and isinstance(item[0], str)
                and isinstance(item[1], dict)
        )

    @staticmethod
    def is_schema(item: PRIMITIVE_ITEM) -> bool:
        return isinstance(item, (widgets.UserInput, InputGroup))

    @staticmethod
    def is_group(item: PRIMITIVE_ITEM) -> bool:
        return isinstance(item, dict) and ('fields' in item or 'primitive' in item)
