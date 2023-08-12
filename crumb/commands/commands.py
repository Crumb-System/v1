import argparse
import asyncio
from inspect import iscoroutinefunction
from typing import Type

from crumb.orm import connection as db_connection


class Command:
    name: str
    parser: argparse.ArgumentParser
    help_text: str = 'Write command help text'
    need_db_connection: bool = True

    def __init__(self):
        self.parser = argparse.ArgumentParser(usage=self.help_text)

    def __call__(self):
        self.add_arguments()
        handle_kwargs = self.parser.parse_args().__dict__
        if iscoroutinefunction(self.handle):
            if self.need_db_connection:
                async def exec_run():
                    await db_connection.init()
                    await self.handle(**handle_kwargs)
                    await db_connection.close()
                asyncio.run(exec_run())
            else:
                asyncio.run(self.handle(**handle_kwargs))
        else:
            self.handle(**handle_kwargs)

    def add_arguments(self):
        pass

    def handle(self, **kwargs):
        raise NotImplementedError('Хоть что-то напиши')


def register_command(cmd: Type[Command]):
    all_commands[cmd.name] = cmd()


def run_command(name: str):
    command = all_commands.get(name)
    if command:
        command()
    else:
        n = '\n'
        print(f'Доступные команды: \n{n.join(all_commands.keys())}')


all_commands: dict[str, Command] = {}
