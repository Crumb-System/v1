import json
from typing import Type

from crumb.commands import Command, register_command
from crumb.exceptions import ObjectErrors
from crumb.users.repository import BaseUserRepository
from crumb.utils import get_user_repository


@register_command
class CreateSuperUser(Command):
    name = 'createsuperuser'
    need_db_connection = True

    def add_arguments(self):
        self.parser.add_argument('-u', '--username', required=True)
        self.parser.add_argument('-p', '--password', required=True)

    async def handle(self, username: str, password: str):
        user_repository: Type["BaseUserRepository"] = get_user_repository()
        try:
            user = await user_repository().create_superuser(username=username, password=password, re_password=password)
            print(f'Суперпользователь {user.username} успешно создан')
        except ObjectErrors as e:
            print(json.dumps(e.to_error(), indent=4, ensure_ascii=False))
