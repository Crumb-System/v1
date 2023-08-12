from dataclasses import dataclass

from flet import TextOverflow

from . import StrInputWidget, StrInput


class TextInputWidget(StrInputWidget):

    def __init__(
            self,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.input.multiline = True
        self.input.shift_enter = True
        self.text.overflow = TextOverflow.FADE
        self.__finalize_init__()


@dataclass
class TextInput(StrInput[TextInputWidget]):
    width: int | float = 500
    height: int | float = 200
    resize_width: bool = True
    resize_height: bool = True

    @property
    def widget_type(self):
        return TextInputWidget
