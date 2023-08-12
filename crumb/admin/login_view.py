from typing import Type, TYPE_CHECKING

from flet import (
    UserControl, Column, Container,
    ElevatedButton, Text,
    MainAxisAlignment, CrossAxisAlignment, alignment
)

from .forms import SimpleInputForm, FormSchema, widgets
from .layout.box import Box
from ..exceptions import NotAuthenticated

if TYPE_CHECKING:
    from .app import CRuMbAdmin


class LoginView(UserControl, Box):
    def __init__(self, app_cls: Type["CRuMbAdmin"]):
        UserControl.__init__(self, expand=True)
        self.app_cls = app_cls

    def build(self):
        return Container(
            content=LoginForm(box=self),
            alignment=alignment.center,
            border_radius=12,
            bgcolor='white'
        )


def clear_error_text(widget: widgets.UserInputWidget):
    widget.form.error_text.value = ''


class LoginForm(SimpleInputForm):
    schema = FormSchema(
        widgets.StrInput(
            name='username',
            label='Логин',
            max_length=30,
            width=350,
            on_value_change=clear_error_text
        ),
        widgets.StrInput(
            name='password',
            label='Пароль',
            max_length=30,
            is_password=True,
            width=350,
            on_value_change=clear_error_text
        )
    )
    box: LoginView

    def __init__(
            self,
            box: LoginView
    ):
        super().__init__(box=box)
        self.error_text = Text(color='error')

    def build(self):
        return Column(
            controls=[
                Text(self.box.app_cls.title, size=40, color='primary'),
                self.error_text,
                super().build(),
                self.login_btn()
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )

    def login_btn(self):
        return ElevatedButton('Войти', on_click=self.login)

    async def set_error_text(self, value: str):
        self.error_text.value = value
        await self.update_async()

    async def login(self, e=None):
        if not self.form_is_valid():
            await self.update_async()
            return
        try:
            user = await self.box.app_cls.user_repository().authenticate(**self.cleaned_data())
        except NotAuthenticated:
            return await self.set_error_text('Нет пользователя с таким логином или паролем')
        if not user.is_active:
            return await self.set_error_text('Пользователь помечен как неактивный')
        if not user.can_login_admin:
            return await self.set_error_text('Недостаточно прав для входа')
        page = self.page
        await page.clean_async()
        await page.add_async(self.box.app_cls(page=page, user=user))
