from typing import cast, TypeVar

from crumb.admin.forms import Primitive, widgets, SimpleInputForm
from crumb.admin.layout import BOX
from crumb.admin.resources import DirectoryResource

from crumb.users.repository import USER_MODEL
from .forms import UserEditForm, PasswordChangeForm
from .repository import BaseUserRepository

__all__ = ["BaseUserResource"]

USER_REPO = TypeVar('USER_REPO', bound=BaseUserRepository)


def match_passwords(widget: widgets.UserInputWidget):
    form = cast(SimpleInputForm, widget.parent)
    if widget.final_value != form.fields_map['password'].final_value:
        widget.set_error_text('Пароли не совпадают')


class BaseUserResource(DirectoryResource[USER_REPO]):
    list_form_primitive = Primitive(
        ('username', {'width': 180}),
        ('is_superuser', {'width': 200}),
        ('can_login_admin', {'width': 300}),
        ('is_active', {'width': 120}),
        ('created_at', {'width': 250})
    )

    create_form_primitive = Primitive(
        'username',
        ('password', {
            "required": False,
            "null": True,
            "empty_as_none": True,
            "ignore_if_none": True
        }),
        ('re_password', {
            "required": False,
            "null": True,
            "empty_as_none": True,
            "ignore_if_none": True,
            "on_value_change": match_passwords
        }),
    )

    edit_model_form = UserEditForm
    edit_form_primitive = Primitive(
        'username',
        'created_at',
        ('is_superuser', {'ignore': True, 'editable': False}),
        ('can_login_admin', {'ignore': True, 'editable': False}),
        ('is_active', {'ignore': True, 'editable': False}),
    )
    password_change_primitive = Primitive(
        ('password', {}),
        ('re_password', {"on_value_change": match_passwords}),
    )

    def get_password_change_form(
            self,
            box: "BOX",
            user: USER_MODEL,
    ) -> PasswordChangeForm:
        form = PasswordChangeForm(
            resource=self,
            box=box,
            primitive=self.password_change_primitive,
            user=user
        )
        return self.with_tab_title(form, 'password_change', user=user)

    def _tab_title_password_change(self, user: USER_MODEL) -> str:
        return self.translation.password_change(user=user)

    def _methods(self):
        methods = super()._methods()
        if not self.repository.READ_ONLY_REPOSITORY:
            methods['password_change'] = self.get_password_change_form
        return methods
