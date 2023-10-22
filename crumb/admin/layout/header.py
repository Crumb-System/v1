from typing import TYPE_CHECKING

from flet import (
    Container, Row, Icon, icons,
    Text, PopupMenuButton, PopupMenuItem,
    MainAxisAlignment, padding
)

from .payload import PayloadInfo

if TYPE_CHECKING:
    from ..app import CRuMbAdmin


__all__ = ["Header"]


class Header(Container):
    app: "CRuMbAdmin"

    def __init__(self, app: "CRuMbAdmin"):
        super().__init__(bgcolor='primary', padding=padding.symmetric(horizontal=10))
        self.app = app
        self.content = Row(
            height=40,
            controls=[
                Text(app.title, color='background', size=20),
                Row([
                    Text(app.user.username, color='background', size=16),
                    PopupMenuButton(
                        content=Icon(icons.MORE_VERT_ROUNDED, color='background'),
                        items=[
                            PopupMenuItem(text="Сменить пароль", on_click=self.open_current_user_password_change_form),
                            # PopupMenuItem(),  # divider
                            PopupMenuItem(text="Выход", on_click=self.app.logout),
                        ],
                    )
                ])
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
        )

    async def open_current_user_password_change_form(self, e=None):
        await self.app.open(PayloadInfo(
            entity=self.app.user_resource.entity(),
            method='password_change',
            query={'user': self.app.user}
        ))
