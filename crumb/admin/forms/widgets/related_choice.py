from dataclasses import dataclass, field
from typing import Optional, Any

from flet import Container, Row, Text, Icon, icons, padding, alignment, TextOverflow, MainAxisAlignment

from crumb.orm import BaseModel
from crumb.types import PK
from crumb.admin.layout import PayloadInfo
from crumb.admin.forms.widgets import UserInputWidget, UserInput
from crumb.admin.exceptions import InputValidationError
from ..widget_containers import BaseWidgetContainer, SimpleWidgetContainer


# TODO: переделать на dropdown с элементами, подбираемыми по вводу
class RelatedChoiceWidget(UserInputWidget[PK], Container):

    real_value: Optional[BaseModel]

    @property
    def final_value(self) -> Optional[PK]:
        return self.real_value.pk if self.real_value else None

    def __init__(self, entity: str, method: str, query: dict[str, Any], **kwargs):
        Container.__init__(self, alignment=alignment.center_left)
        UserInputWidget.__init__(self, **kwargs)

        self.entity = entity
        self.method = method
        self.query = query

        self.text = Text(size=14, no_wrap=True, overflow=TextOverflow.ELLIPSIS)
        self.content = Row(
            controls=[self.text, Icon(icons.FORMAT_LIST_BULLETED_OUTLINED)],
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )
        self.on_start_changing = self.open_choice
        self.__finalize_init__()

    def apply_container(self, container: BaseWidgetContainer):
        super().apply_container(container)
        if isinstance(self.container, SimpleWidgetContainer):
            self.padding = padding.symmetric(horizontal=12)

    def set_value(self, value: Optional[BaseModel], initial: bool = False):
        assert value is None or isinstance(value, BaseModel), f'{self.name}, {value}'
        self.real_value = value
        self.text.value = str(self.real_value) if self.real_value else ''

    def _validate(self) -> None:
        if self.required and self.real_value is None:
            raise InputValidationError('Обязательное поле')

    async def update_real_value(self, new_value: Optional[BaseModel]) -> None:
        self.set_value(new_value)

    async def on_cancel_choice(self):
        await self.end_change_event_handler()

    async def open_choice(self, e):
        await self.form.box.add_modal(info=PayloadInfo(
            entity=self.entity,
            method=self.method,
            query={
                'make_choice': self.update_real_value,
                'BOX_on_close': self.on_cancel_choice,
                **self.query
            }
        ))


@dataclass
class RelatedChoice(UserInput[RelatedChoiceWidget]):
    entity: str = ''
    method: str = 'choice'
    query: dict[str, Any] = field(default_factory=dict)

    @property
    def widget_type(self):
        return RelatedChoiceWidget
