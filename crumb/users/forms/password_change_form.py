from flet import Row, ElevatedButton

from crumb.admin.forms import ModelInputForm
from crumb.admin.forms import Primitive
from crumb.admin.layout import BOX
from crumb.admin.resources import Resource
from crumb.enums import NotifyStatus
from crumb.exceptions import ObjectErrors
from crumb.users.repository import USER_MODEL


class PasswordChangeForm(ModelInputForm):

    def __init__(
            self,
            resource: "Resource",
            box: "BOX",
            primitive: "Primitive",
            *,
            user: USER_MODEL
    ):
        super().__init__(
            resource=resource,
            box=box,
            primitive=primitive
        )
        self.user = user

    def get_action_bar(self) -> Row:
        return Row([self.submit_btn()])

    def submit_btn(self):
        return ElevatedButton('Подтвердить', on_click=self.on_click_submit)

    async def change_password(self) -> bool:
        if not self.form_is_valid():
            await self.update_async()
            return False
        data = self.cleaned_data()
        password = data['password']
        re_password = data['re_password']
        try:
            await self.app.user_repository(instance=self.user).change_password(
                password=password,
                re_password=re_password,
            )
            return True
        except ObjectErrors as err:
            self.set_object_errors(err)
            await self.update_async()
            await self.notify_fix_errors(err)
            return False

    async def on_click_submit(self, e=None):
        async with self.app.error_tracker():
            success = await self.change_password()
            if success:
                await self.app.notify(f'Пароль пользователя {self.user} успешно изменён', NotifyStatus.SUCCESS)
                await self.box.close()
