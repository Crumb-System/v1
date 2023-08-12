from typing import TYPE_CHECKING, Union, Optional, Literal
from dataclasses import dataclass, field

from flet import Control, Row, Column, CrossAxisAlignment

if TYPE_CHECKING:
    from .widgets import UserInput


@dataclass
class InputGroup:
    name: str
    fields: list[Union["UserInput", "InputGroup"], ...] = field(default_factory=list)
    label: Optional[str] = field(default=None)
    direction: Literal['horizontal', 'vertical'] = field(default='horizontal')

    def __iter__(self):
        return self.fields.__iter__()

    def to_control(self, children: list[Control]) -> Row | Column:
        if self.direction == 'horizontal':
            return Row(controls=children, spacing=30, vertical_alignment=CrossAxisAlignment.START)
        else:
            return Column(controls=children)

    def add_field(self, item: Union["UserInput", "InputGroup"]) -> None:
        self.fields.append(item)


class FormSchema:
    items: list[Union["UserInput", "InputGroup"]]

    def __init__(self, *items: Union["UserInput", "InputGroup"]):
        self.items = []
        for item in items:
            self.add_item(item)

    def add_item(self, item: Union["UserInput", "InputGroup"]):
        self.items.append(item)

    def __iter__(self):
        return self.items.__iter__()
