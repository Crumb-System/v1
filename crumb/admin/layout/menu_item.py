from typing import TYPE_CHECKING, Optional

from flet import ListTile, Text, Icon, ControlEvent


if TYPE_CHECKING:
    from crumb.admin.app import CRuMbAdmin
    from .payload import PayloadInfo
    from .menu_group import MenuGroup


class MenuItem(ListTile):

    def __init__(
            self,
            app: "CRuMbAdmin",
            info: "PayloadInfo",
            parent: Optional["MenuGroup"] = None,
    ):
        super().__init__(
            dense=True,
            on_click=self.handle_click,
        )
        self.app = app
        self.parent = parent
        self.info = info
        resource = self.app.find_resource(self.info.entity)
        extra = self.info.extra or {}
        icon = extra.get('icon', resource.ICON)
        label = extra.get('label', resource.name_plural)
        self.leading = Icon(icon, size=24)
        self.title = Text(label, no_wrap=True, size=14)

    async def handle_click(self, e: ControlEvent):
        sidebar = self.app.sidebar
        if sidebar.expanded and not sidebar.pinned:
            sidebar.expanded = False
            sidebar.extend_groups()
        await self.app.open(self.info)

    def minimize(self):
        self.title.visible = False

    def maximize(self):
        self.title.visible = True
