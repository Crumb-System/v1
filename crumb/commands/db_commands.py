import subprocess
import platform

from crumb.commands import Command, register_command
from crumb.utils import get_settings

db_config: dict[str, ...] = get_settings().DATABASE
default_aerich_exe = '.venv/bin/aerich' if platform.system() == 'Linux' else '.venv/Scripts/aerich.exe'


@register_command
class DbCommands(Command):
    name = 'db'
    need_db_connection = False

    def add_arguments(self):
        self.parser.add_argument('--exe', default=default_aerich_exe, help='aerich.exe path')
        self.parser.add_argument('--apps', nargs='*', default=list(db_config['apps']), help='Список приложений')
        self.parser.add_argument('-i', '--init', action='store_true', help='Создать первые миграции')
        self.parser.add_argument('-m', '--migrate', action='store_true', help='Зафиксировать миграции')
        self.parser.add_argument('-n', '--name', default='upgrade', help='Имя файла миграции')
        self.parser.add_argument('-u', '--upgrade', action='store_true', help='Провести непримененные миграции')

    async def handle(
            self,
            exe: str,
            apps: list[str],
            init: bool,
            migrate: bool,
            name: str,
            upgrade: bool,
    ):
        assert all(app in db_config['apps'] for app in apps), 'available apps: ' + ', '.join(db_config['apps'])
        if init:
            for app_name in apps:
                subprocess.run([exe, '--app', app_name, 'init-db'])
        else:
            if migrate:
                for app_name in apps:
                    subprocess.run([exe, '--app', app_name, 'migrate', '--name', name])
            if upgrade:
                for app_name in apps:
                    subprocess.run([exe, '--app', app_name, 'upgrade', '--in-transaction', 'true'])
