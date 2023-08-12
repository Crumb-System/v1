import inspect
from typing import TYPE_CHECKING, Generic, Type, Callable, Coroutine, Any, TypeVar

from flet import Control, icons

from crumb.repository import REPOSITORY

if TYPE_CHECKING:
    from crumb.admin.app import CRuMbAdmin
    from crumb.admin.layout import BOX


__all__ = ["Resource", "ValuesListResource"]

C = TypeVar('C', bound=Control)


class Resource(Generic[REPOSITORY]):
    repository: Type[REPOSITORY]
    ICON = icons.SPORTS_GYMNASTICS

    def __init__(self, app: "CRuMbAdmin") -> None:
        self.app = app
        self.translation = self.app.translation.get_entity(self.entity())

    def relative_entity(self, field_name: str) -> str:
        return self.repository.repository_of(field_name).entity()

    def relative_resource(self, field_name: str) -> "Resource":
        return self.app.find_resource(self.relative_entity(field_name))

    @classmethod
    def entity(cls) -> str:
        return cls.repository.entity()

    @classmethod
    def default_method(cls) -> str:
        pass

    def _methods(self) -> dict[str, Callable[["BOX", ...], Control | Coroutine[Any, Any, Control]]]:
        return {}

    @property
    def methods(self) -> dict[str, Callable[["BOX", ...], Control | Coroutine[Any, Any, Control]]]:
        if not hasattr(self, '_cached_methods'):
            setattr(self, '_cached_methods', self._methods())
        return getattr(self, '_cached_methods')

    async def get_payload(self, box: "BOX", method: str, **query) -> Control:
        callback = self.methods[method]
        if inspect.iscoroutinefunction(callback):
            payload = await callback(box, **query)
        else:
            payload = callback(box, **query)
        return payload

    # Частые переводы
    @property
    def name(self) -> str:
        return self.translation.name

    @property
    def name_plural(self) -> str:
        return self.translation.name_plural

    def translate_field(self, field_name: str) -> str:
        translation = self.translation.field(field_name)
        if translation is None:
            field_type = self.repository.get_field_type(field_name)
            if field_type.is_single_relation():
                translation = self.app.translation.get_entity(self.relative_entity(field_name)).name
            elif field_type.is_multiple_relation():
                translation = self.app.translation.get_entity(self.relative_entity(field_name)).name_plural
            else:
                translation = field_name
        return translation

    # Функции для установки названия вкладок с мультиязычность и параметрами.
    def with_tab_title(self, control: C, method: str, **kwargs) -> C:
        control.__tab_title__ = getattr(self, f'_tab_title_{method}')(**kwargs)
        return control

    # Функции для сравнения параметров вкладок.
    # Если True, то вкладка создаваться не будет и откроется существующая
    # Если False, то создастся новая вкладка
    def compare_tab(self, method: str, query1: dict[str, Any], query2: dict[str, Any]) -> bool:
        return getattr(self, f'_compare_tab_{method}')(query1, query2)


class ValuesListResource(Resource):
    pass
