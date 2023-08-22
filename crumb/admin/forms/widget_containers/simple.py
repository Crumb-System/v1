from typing import Optional
from math import pi

from flet import (
    Stack, Container, GestureDetector, Text, Icon,
    icons, border, padding, margin, MouseCursor,
    DragStartEvent, DragUpdateEvent
)

from .base import BaseWidgetContainer, W


class SimpleWidgetContainer(BaseWidgetContainer[W], Stack):
    resize_start_global_x: float
    resize_start_global_y: float
    resize_start_width: int | float
    resize_start_height: int | float

    def __init__(self, widget: W):
        Stack.__init__(self)
        BaseWidgetContainer.__init__(self, widget=widget)

        self.container = Container(border_radius=12, margin=margin.only(top=5))
        if self.widget.editable:
            self.gesture_detector = GestureDetector(
                content=self.widget_with_tooltip,
                mouse_cursor=MouseCursor.CLICK
            )
            self.gesture_detector.on_tap_up = self.widget.start_change_event_handler
            self.container.content = self.gesture_detector
        else:
            self.container.content = self.widget_with_tooltip

        self._label = Text(
            value=self.widget.label_text or '',
            size=12,
            color='primary'
        )
        self._label_container = Container(
            content=self._label,
            padding=padding.symmetric(horizontal=3),
            bgcolor='background',
            left=10,
            offset=(0, -0.25),
            visible=not not self.widget.label_text
        )
        self.controls = [self.container, self._label_container]
        self.resize_zone: Optional[GestureDetector] = None
        if self.widget.resize_width or self.widget.resize_height:
            self.make_resizable()
        self.widget.apply_container(self)

    def get_width(self) -> int | float:
        return self.container.width

    def set_width(self, v: int | float):
        self.container.width = v

    def get_height(self) -> int | float:
        return self.container.height

    def set_height(self, v: int | float):
        self.container.height = v

    def make_resizable(self) -> None:
        self.resize_zone = GestureDetector(
            right=0,
            bottom=0,
            offset=(0.4, 0.4),
            content=Icon(icons.ARROW_RIGHT_ROUNDED, size=15, rotate=pi/4, color='primary'),
            mouse_cursor=MouseCursor.RESIZE_DOWN_RIGHT,
            drag_interval=100,
            on_pan_start=self.on_resize_start,
            on_pan_update=self.on_resize_update,
        )
        self.controls.append(self.resize_zone)

    def on_resize_start(self, e: DragStartEvent):
        self.resize_start_global_x = e.global_x
        self.resize_start_global_y = e.global_y
        self.resize_start_width = self.get_width()
        self.resize_start_height = self.get_height()

    async def on_resize_update(self, e: DragUpdateEvent):
        if self.widget.resize_width:
            new_width = self.resize_start_width + (e.global_x - self.resize_start_global_x)
            new_width = max(new_width, self.widget.min_width or 50)
            new_width = min(new_width, self.widget.max_width or 4000)
            self.set_width(new_width)

        if self.widget.resize_height:
            new_height = self.resize_start_height + (e.global_y - self.resize_start_global_y)
            new_height = max(new_height, self.widget.min_height or 50)
            new_height = min(new_height, self.widget.max_height or 4000)
            self.set_height(new_height)

        await self.update_async()

    @property
    def with_label(self) -> bool:
        return self._label.visible

    @with_label.setter
    def with_label(self, v: bool):
        self._label.visible = v

    @property
    def with_border(self) -> bool:
        return self._with_border

    @with_border.setter
    def with_border(self, v: bool):
        self._with_border = v
        if self._with_border:
            self.set_normal_borders()
        else:
            self.container.border = None

    def set_normal_borders(self):
        self.container.border = border.all(1, 'primary')

    def set_error_borders(self):
        self.container.border = border.all(1, 'error')

    def set_error_text(self, text: str):
        super().set_error_text(text)
        if self.with_border:
            self.set_error_borders()
        if self.resize_zone:
            self.resize_zone.content.color = 'error'
        if self.with_label:
            self._label.color = 'error'

    def rm_error(self):
        super().rm_error()
        if self.with_border:
            self.set_normal_borders()
        if self.resize_zone:
            self.resize_zone.content.color = 'primary'
        if self.with_label:
            self._label.color = 'primary'
