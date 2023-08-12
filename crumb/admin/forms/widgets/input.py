from dataclasses import dataclass
from typing import Literal

from flet import Container, Stack, Text, TextField, InputBorder, TextOverflow, alignment, padding

from .user_input import UserInputWidget, UserInput, T, _I
from ..widget_containers import BaseWidgetContainer, SimpleWidgetContainer


class InputWidget(UserInputWidget[T], Container):

    def __init__(
            self,
            **kwargs
    ):
        self.input = TextField(
            text_size=14,
            dense=True,
            border=InputBorder.NONE,
            on_blur=self.end_change_event_handler,
            content_padding=0
        )
        self.text = Text(size=14, no_wrap=True, overflow=TextOverflow.ELLIPSIS)
        Container.__init__(
            self,
            content=Stack(controls=[self.text, self.input]),
            alignment=alignment.center_left
        )

        UserInputWidget.__init__(self, **kwargs)

        self.on_start_changing = self.focus_on_start_changing
        self.on_end_changing = self.set_value_on_end_changing

    async def focus_on_start_changing(self, e=None):
        await self.input.focus_async()

    def set_value_on_end_changing(self, e=None):
        self.set_value(self.input.value)

    def apply_container(self, container: BaseWidgetContainer):
        super().apply_container(container)
        if isinstance(self.container, SimpleWidgetContainer):
            self.padding = padding.symmetric(horizontal=12)

    def set_mode(self, v: Literal['read', 'write']):
        super().set_mode(v)
        if v == 'read':
            self.text.visible = True
            self.input.visible = False
        else:
            self.text.visible = False
            self.input.visible = True

    @property
    def value(self):
        return self.input.value

    @value.setter
    def value(self, v: str):
        self.text.value = v
        self.input.value = v

    @property
    def editable(self):
        return not self.input.read_only

    @editable.setter
    def editable(self, v: bool):
        self.input.read_only = not v


@dataclass
class Input(UserInput[_I]):
    pass
