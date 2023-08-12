from dataclasses import dataclass
from enum import Enum
from typing import Type, Optional, TypeVar, Literal, Callable, Coroutine, Sequence, TYPE_CHECKING

from flet import Container, Row, Text, Icon, ListView as FletListView,\
    icons, TextOverflow, alignment, padding, MainAxisAlignment, ControlEvent, TapEvent

from crumb.utils import default_if_none
from .user_input import UserInputWidget, UserInput
from ..widget_containers import BaseWidgetContainer, SimpleWidgetContainer
from ...exceptions import InputValidationError

if TYPE_CHECKING:
    from crumb.admin.layout import Popover


EMPTY_TEXT = ""
E = TypeVar('E', bound=Enum)


class EnumChoiceWidget(UserInputWidget[E], Container):

    @property
    def final_value(self) -> Optional[E]:
        return self.value

    def __init__(
            self,
            *,
            enum_type: Type[E] = None,
            **kwargs
    ):
        self.text = Text(size=14, no_wrap=True, overflow=TextOverflow.ELLIPSIS)
        self.dropdown = EnumChoiceDropdown(widget=self)
        Container.__init__(
            self,
            content=Row(
                controls=[self.text, Icon(icons.ARROW_DROP_DOWN_OUTLINED)],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            alignment=alignment.center_left
        )

        UserInputWidget.__init__(self, **kwargs)
        assert enum_type is not None
        self.enum_type = enum_type

        self.translations = self.form.app.translation.get_enum_translations(enum_type)
        self.dropdown.options = [(x, self.translations[x]) for x in self.enum_type]
        if not self.required:
            self.dropdown.add_option(value=None, label=EMPTY_TEXT, index=0)

        self.__finalize_init__()

    def apply_container(self, container: BaseWidgetContainer):
        super().apply_container(container)
        if isinstance(container, SimpleWidgetContainer):
            self.padding = padding.symmetric(horizontal=12)

    def set_value(self, value: Optional[E], initial: bool = False):
        assert value is None or isinstance(value, self.enum_type)
        self.value = value
        if self.value is None:
            self.text.value = EMPTY_TEXT
        else:
            self.text.value = self.translations[self.value]

    def _validate(self) -> None:
        if self.required and self.value is None:
            raise InputValidationError('Обязательное поле')

    def set_mode(self, v: Literal['read', 'write']):
        super().set_mode(v)

    async def start_change_event_handler(self, e: TapEvent = None):
        assert isinstance(e, TapEvent)
        self.dropdown.top = e.global_y - e.local_y - 2
        self.dropdown.left = e.global_x - e.local_x - 2
        self.dropdown.width = self.container.get_width()
        popover = await self.form.box.app.add_popover(
            self.dropdown,
            on_close=self.end_change_event_handler,
        )
        self.dropdown.popover = popover
        await super().start_change_event_handler(e)


@dataclass
class EnumChoice(UserInput[EnumChoiceWidget[E]]):
    enum_type: Type[E] = None

    @property
    def widget_type(self):
        return EnumChoiceWidget


class EnumChoiceDropdown(Container):
    popover: "Popover"

    def __init__(
            self,
            widget: "EnumChoiceWidget",
            options: list["EnumChoiceDropdownOption"] = None
    ):
        Container.__init__(
            self,
            border_radius=12,
            bgcolor='#F4F6F8',
            padding=padding.symmetric(vertical=10)
        )
        self.widget = widget
        self.content = self.list = FletListView()
        self.options = default_if_none(options, [])

    def add_option(self, value: Optional[Enum], label: str, index: int = -1):
        opt = EnumChoiceDropdownOption(
            value=value,
            label=label,
            on_click=self.select_option
        )
        if index == -1:
            self.options.append(opt)
        else:
            self.options.insert(index, opt)
        self.list.height = min((300, len(self.options) * 30))

    async def select_option(self, e: ControlEvent):
        opt: EnumChoiceDropdownOption = e.control
        self.widget.set_value(opt.value)
        await self.popover.close()
        del self.popover

    @property
    def options(self) -> list["EnumChoiceDropdownOption"]:
        return self.list.controls

    @options.setter
    def options(self, v: Sequence[tuple[Enum, str]]):
        self.list.controls = []
        self.list.height = 0
        for opt in v:
            self.add_option(opt[0], opt[1])


class EnumChoiceDropdownOption(Container):
    def __init__(self, value: Enum, label: str, on_click: Callable[[ControlEvent], Coroutine[..., ..., None] | None]):
        super().__init__(
            content=Text(label, size=14, overflow=TextOverflow.ELLIPSIS),
            padding=padding.symmetric(horizontal=10),
            alignment=alignment.center_left,
            on_click=on_click,
            height=30,
        )
        self.value = value

