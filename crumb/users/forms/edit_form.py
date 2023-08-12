from flet import Row, ElevatedButton

from crumb.admin.forms import DirectoryInputForm
from crumb.admin.layout import PayloadInfo


class UserEditForm(DirectoryInputForm):
    def get_action_bar(self) -> Row:
        bar = super().get_action_bar()
        bar.controls.append(self.password_change_btn())
        return bar

    def password_change_btn(self):
        return ElevatedButton('Изменить пароль', on_click=self.open_password_change_form)

    async def open_password_change_form(self, e=None):
        await self.box.add_modal(PayloadInfo(
            entity=self.resource.entity(),
            method='password_change',
            query={'user': self.instance}
        ))


