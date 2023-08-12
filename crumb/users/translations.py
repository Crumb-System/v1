from dataclasses import dataclass, field

from crumb.translations.langs import ru, en


class PasswordChangeTranslationMixin:
    _password_change: str
    password_change_template: str = '{self._password_change}: {user}'

    def password_change(self, **kwargs):
        return self.password_change_template.format(self=self, **kwargs)


@dataclass
class RuUserEntityTranslation(PasswordChangeTranslationMixin, ru.Entity):
    name: str = 'Пользователь'
    name_plural: str = 'Пользователи'
    fields: dict[str, str] = field(default_factory=lambda: {
        'username': 'Логин',
        'is_superuser': 'Суперпользователь',
        'can_login_admin': 'Может авторизоваться в админке',
        'is_active': 'Активный',
        'created_at': 'Дата и время создания',
        'password': 'Пароль',
        're_password': 'Повторите пароль',
    })
    _password_change: str = 'Изменение пароля пользователя'


@dataclass
class EnUserEntityTranslation(PasswordChangeTranslationMixin, en.Entity):
    name: str = 'User'
    name_plural: str = 'Users'
    fields: dict[str, str] = field(default_factory=lambda: {
        'username': 'Username',
        'is_superuser': 'Is superuser',
        'can_login_admin': 'Can login admin panel',
        'is_active': 'Is active',
        'created_at': 'Created at',
        'password': 'Password',
        're_password': 'Repeat password',
    })
    _password_change: str = 'User password change'
