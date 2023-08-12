import importlib

from tortoise import Tortoise

from crumb.utils import get_settings


async def init():
    await Tortoise.init(config=get_settings().DATABASE)
    importlib.import_module('configuration.repositories')


async def close():
    await Tortoise.close_connections()
