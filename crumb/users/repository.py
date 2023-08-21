import re
from random import choices
from string import hexdigits
from typing import TypeVar, Optional

from tortoise import timezone
from passlib.context import CryptContext

from crumb.entities.directories import DirectoryRepository
from crumb.exceptions import AnyFieldError, ItemNotFound, NotAuthenticated, ObjectErrors
from crumb.types import DATA

from .model import BaseUser
from ..enums import FieldTypes

PasswordIncorrect = AnyFieldError('password_incorrect', 'Некорректный пароль')
PasswordMismatch = AnyFieldError('password_mismatch', 'Пароли не совпадают')
UsernameEmployed = AnyFieldError('username_employed', 'Пользователь с таким логином уже существует')
UNUSED_PASSWORD_PREFIX = '!'
USER_MODEL = TypeVar("USER_MODEL", bound=BaseUser)


class BaseUserRepository(DirectoryRepository[USER_MODEL]):

    hidden_fields = {'password_hash', 'password_change_dt', 'password_salt'}
    extra_allowed = {
        'password': (FieldTypes.STR, {"is_password": True, 'min_length': 8, 'max_length': 30}),
        're_password': (FieldTypes.STR, {"is_password": True, 'min_length': 8, 'max_length': 30})
    }

    # обязательны 1 буква и цифра; допустимы буквы (латиница), цифры и !@#$%^&*-_=+
    password_pattern = re.compile('^(?=.*[A-Za-z])(?=.*[0-9])[A-Za-z0-9!@#$%^&*-_=+]{8,30}$')
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def _validate_password(
            self,
            value: str,
            data: DATA,
    ) -> None:
        if not self.password_pattern.match(value):
            raise PasswordIncorrect

    async def _validate_re_password(
            self,
            value: str,
            data: DATA,
    ):
        if value != data.get('password'):
            raise PasswordMismatch

    async def _validate_username(
            self,
            value: str,
            data: DATA
    ):
        if self.instance and self.instance.username.lower() == value.lower():
            return
        try:
            await self.get_one(value=value, field_name='username')
            raise UsernameEmployed
        except ItemNotFound:
            pass

    async def handle_create(
            self,
            data: DATA,
            extra_data: DATA
    ) -> USER_MODEL:
        user: USER_MODEL = self.model(**data)
        self.set_password(user, extra_data.get('password'))
        await user.save(force_create=True)
        return user

    async def create_superuser(self, username: str, password: str, re_password: str):
        return await self.create(
            data={'username': username, 'password': password, 're_password': re_password},
            defaults={'is_superuser': True, 'can_login_admin': True, 'is_active': True}
        )

    @classmethod
    def create_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def password_is_unused(cls, password_hash: str) -> bool:
        return password_hash.startswith(UNUSED_PASSWORD_PREFIX)

    @classmethod
    def verify_password(cls, password: str, password_hash: str) -> bool:
        if cls.password_is_unused(password_hash):
            return False
        return cls.pwd_context.verify(password, password_hash)

    @classmethod
    def set_password(cls, user: USER_MODEL, password: Optional[str]):
        user.password_change_dt = timezone.now()
        if password:
            password_hash = cls.create_password_hash(password)
        else:
            random_pwd = ''.join(choices(hexdigits, k=10))
            password_hash = UNUSED_PASSWORD_PREFIX + cls.create_password_hash(random_pwd)
        user.password_hash = password_hash

    async def authenticate(self, username: str, password: str) -> Optional[USER_MODEL]:
        try:
            user = await self.get_one(value=username, field_name='username')
        except ItemNotFound:
            raise NotAuthenticated()
        if not self.verify_password(password, user.password_hash):
            raise NotAuthenticated()
        return user

    async def change_password(self, password: str, re_password: str):
        assert self.instance
        errors = ObjectErrors()
        try:
            await self.validate({
                'password': password,
                're_password': re_password
            })
        except ObjectErrors as e:
            errors.merge(e)

        if errors:
            raise errors

        self.set_password(user=self.instance, password=password)
        await self.instance.save(force_update=True)
