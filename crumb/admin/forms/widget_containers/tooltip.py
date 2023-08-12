from typing import TYPE_CHECKING, Union

from flet import Tooltip, Control, TextStyle, padding, border

if TYPE_CHECKING:
    from crumb.admin.forms.widgets import UserInputWidget


class WidgetTooltip(Tooltip):

    def __init__(
            self,
            content: Union[Control, "UserInputWidget"],
            helper_text: str = None,
    ):
        super().__init__(
            content=content,
            prefer_below=False,
            padding=padding.symmetric(5, 10),
            vertical_offset=20,
            border_radius=5,
        )
        self.helper_text = helper_text
        if self.helper_text:
            self._set_helper_text(self.helper_text)
        else:
            self._make_invisible()

    def _set_helper_text(self, text: str):
        self.message = text
        self.border = border.all(1, '#9b9b9b')
        self.bgcolor = '#f1f1f1'
        self.text_style = TextStyle(color='black')
        self.wait_duration = 0

    def set_error_text(self, text: str):
        self.message = text
        self.border = border.all(1, '#ff3838')
        self.bgcolor = '#ff5d5d'
        self.text_style = TextStyle(color='white')
        self.wait_duration = 0

    def rm_error(self):
        if self.helper_text:
            self._set_helper_text(self.helper_text)
        else:
            self._make_invisible()

    def _make_invisible(self):
        self._set_helper_text('Ты нашёл костыль-пасхалку, поздравляю')
        self.wait_duration = 300_000  # 5 минут
