import importlib
import re
from typing import Any, TypeVar, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from crumb.users.repository import BaseUserRepository
    from crumb.users.resource import BaseUserResource


def remove_extra_spaces(string: str) -> str:
    return remove_extra_spaces.pattern.sub(' ', string)


remove_extra_spaces.pattern = re.compile('\s+')


T = TypeVar('T')


def default_if_none(value: T, default: Any) -> T:
    if value is None:
        return default
    return value


def import_string(dotted_path: str) -> Any:
    """
    Stolen approximately from django. Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import fails.
    """
    from importlib import import_module

    try:
        module_path, class_name = dotted_path.strip(' ').rsplit('.', 1)
    except ValueError as e:
        raise ImportError(f'"{dotted_path}" doesn\'t look like a module path') from e

    module = import_module(module_path)
    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(f'Module "{module_path}" does not define a "{class_name}" attribute') from e


def get_settings():
    return importlib.import_module('configuration.settings')


def get_flet_app():
    return import_string(get_settings().FLET_APP)


def get_app_translations():
    tr_path = getattr(get_settings(), 'APP_TRANSLATIONS', 'configuration.translations.app_translations')
    return import_string(tr_path)


def get_user_repository() -> Type["BaseUserRepository"]:
    repo_path = getattr(get_settings(), 'USER_REPOSITORY', 'configuration.directories.users.repository.UserRepository')
    return import_string(repo_path)


def get_user_resource() -> Type["BaseUserResource"]:
    resource_path = getattr(get_settings(), 'USER_RESOURCE', 'configuration.directories.users.resource.UserResource')
    return import_string(resource_path)
