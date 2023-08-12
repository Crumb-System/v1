from typing import TYPE_CHECKING, Type, Optional
from math import pi

from flet import ListTile, Icon, Text, Column, Container, padding, icons, Rotate

from .menu_item import MenuItem

if TYPE_CHECKING:
    from crumb.admin.app import CRuMbAdmin
    from .payload import PayloadInfo


class MenuGroup(Column):
    icon: str
    label: str
    items_info: list["PayloadInfo"] = ()
    subgroups: Optional[tuple[Type["MenuGroup"]]] = ()

    def __init__(
            self,
            app: "CRuMbAdmin",
            parent: "MenuGroup" = None,
    ):
        super().__init__(spacing=0)
        self.app = app
        self.parent = parent

        self.chevron = Icon(icons.CHEVRON_RIGHT, size=20, rotate=Rotate(0), animate_rotation=100)
        self.root = ListTile(
            leading=Icon(self.icon, size=24),
            title=Text(self.label, no_wrap=True, size=14),
            trailing=self.chevron,
            dense=True,
            on_click=self.handle_click,
        )

        self.children = []
        for group_cls in self.subgroups:
            group = group_cls(app=self.app, parent=self)
            if group.children:
                self.children.append(group)
        for item_info in self.items_info:
            self.children.append(MenuItem(
                app=self.app,
                info=item_info,
                parent=self
            ))

        self.children_container = Container(
            Column(self.children, spacing=0),
            padding=padding.only(left=16),
            animate=100
        )

        self.controls = [
            self.root,
            self.children_container
        ]

        self.extended = False

    async def handle_click(self, e=None):
        self.extended = not self.extended
        sidebar = self.app.sidebar
        if not sidebar.expanded and not sidebar.pinned:
            sidebar.expanded = True
        await sidebar.update_async()

    @classmethod
    def add_item_info(cls, info: "PayloadInfo"):
        if isinstance(cls.items_info, tuple):
            cls.items_info = []
        cls.items_info.append(info)

    @property
    def extended(self) -> bool:
        return self._extended

    @extended.setter
    def extended(self, v: bool):
        self._extended = v
        if v:
            self.children_container.visible = True
            self.chevron.rotate.angle = pi / 2
        else:
            self.children_container.visible = False
            self.chevron.rotate.angle = 0

    def minimize(self):
        self.root.title.visible = False
        self.children_container.padding.left = 4
        self.root.trailing.visible = False
        for child in self.children:
            child.minimize()

    def maximize(self):
        self.root.title.visible = True
        self.children_container.padding.left = 16
        self.root.trailing.visible = True
        for child in self.children:
            child.maximize()
