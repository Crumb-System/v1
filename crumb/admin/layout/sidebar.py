from typing import TYPE_CHECKING, Optional

from flet import Container, Column
import flet as ft

from .btn_pin import BtnPin
from .menu_item import MenuItem

if TYPE_CHECKING:
    from ..app import CRuMbAdmin


__all__ = ["Sidebar"]


class Sidebar(Container):
    items: list[MenuItem]
    app: "CRuMbAdmin"

    active: Optional[MenuItem]

    def __init__(self, app: "CRuMbAdmin"):

        super().__init__(
            bgcolor='white',
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            animate=100,
        )

        self.app = app
        self.btn_pin = BtnPin(pinned=False, sidebar=self)
        self.children = []
        for group_cls in self.app.menu_groups:
            group = group_cls(app)
            if group.children:
                self.children.append(group)

        self.content = Column([
            Container(
                content=Column(self.children, scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=0),
                expand=True,
                animate=100
            ),
            self.btn_pin
        ], spacing=0)

        self.active = None
        self.expanded = False

    @property
    def pinned(self) -> bool:
        return self.btn_pin.pinned

    def minimize(self):
        self.width = 50
        for child in self.children:
            child.minimize()
        self.btn_pin.minimize()

    def maximize(self):
        self.width = 250
        for child in self.children:
            child.maximize()
        self.btn_pin.maximize()

    @property
    def expanded(self) -> bool:
        return self._expanded

    @expanded.setter
    def expanded(self, v: bool):
        if hasattr(self, '_expanded') and v == self.expanded:
            return
        self._expanded = v
        self.maximize() if self.expanded else self.minimize()

    def extend_groups(self):
        for group in self.children:
            group.extended = False
