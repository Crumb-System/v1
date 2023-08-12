from typing import Callable

from flet import IconButton, icons, ControlEvent


class CloseButton(IconButton):
    def __init__(
            self,
            on_click: Callable[[ControlEvent], ...],
            size: int | float = 30,
    ):
        super().__init__(
            icon=icons.CLOSE_ROUNDED,
            icon_size=size / 2,
            height=size,
            width=size,
            on_click=on_click,
        )
