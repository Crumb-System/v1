import asyncio
import importlib
from contextlib import asynccontextmanager
from os import getenv
from pathlib import Path
from typing import Type, TypeVar, Any, Callable, Coroutine, TYPE_CHECKING, ClassVar

from flet import (
    Page, UserControl, Control, Column, Row, Text,
    Theme, ColorScheme,
    SnackBar, ControlEvent,
    app as flet_app
)

from crumb.enums import NotifyStatus
from crumb.translations.app_translation import AppTranslation
from crumb.orm import connection as db_connection
from crumb.admin.layout import Header, TabsBar, PayloadInfo, Sidebar, MenuGroup, ContentsBoxContainer, Popover, Popup
from crumb.admin.resources import Resource

from .components.errors import UnhandledErrorContainer
from .login_view import LoginView
from ..utils import import_string, get_settings

if TYPE_CHECKING:
    from crumb.users.repository import BaseUserRepository, USER_MODEL

RESOURCE = TypeVar("RESOURCE", bound=Resource)


class CRuMbAdmin(UserControl):
    _resources: ClassVar[dict[str, Type["Resource"]]] = {}
    title: ClassVar[str] = 'CRuMb Admin'
    menu_groups: ClassVar[list[Type[MenuGroup]]] = []
    translations: ClassVar[AppTranslation] = import_string(get_settings().APP_TRANSLATIONS)
    user_repository: ClassVar[Type["BaseUserRepository"]]

    def __init__(self, page: Page, user: "USER_MODEL"):
        super().__init__(expand=True)  # чтобы вложенные элементы тоже расширялись

        self.user = user
        self.translation = self.translations.get('ru')
        self._init_resources()
        self.page = page

        self.appbar = Header(app=self)
        self.tabs_bar = TabsBar(app=self)
        self.sidebar = Sidebar(app=self)
        self.content_box_container = ContentsBoxContainer(app=self)

    def _init_resources(self) -> None:
        self._inited_resources = {entity: res(self) for entity, res in self._resources.items()}

    def build(self):
        return Column(
            controls=[
                self.appbar,
                self.tabs_bar,
                Row(
                    controls=[
                        self.sidebar,
                        self.content_box_container,
                    ],
                    spacing=0,
                    expand=True
                )
            ],
            spacing=0,
        )

    @classmethod
    def register(
            cls,
            present_in: tuple[Type["MenuGroup"] | tuple[Type["MenuGroup"], dict[str, Any]], ...] = ()
    ):
        def wrapper(resource: Type[RESOURCE]) -> Type[RESOURCE]:
            cls.register_resource(resource, present_in=present_in)
            return resource
        return wrapper

    @classmethod
    def register_resource(
            cls,
            resource: Type["Resource"],
            present_in: tuple[Type["MenuGroup"] | tuple[Type["MenuGroup"], dict[str, Any]], ...] = ()
    ) -> None:
        for group in present_in:
            if isinstance(group, tuple) and len(group) == 2:
                group, extra = group
                if not issubclass(group, MenuGroup) or not isinstance(extra, dict):
                    raise ValueError(f'Что-то не то передал: {group=}, {extra=}')
                method = extra.pop('method') if 'method' in extra else resource.default_method()
                query = extra.pop('query') if 'query' in extra else {}
                group.add_item_info(PayloadInfo(
                    entity=resource.entity(),
                    method=method,
                    query=query,
                    extra=extra,
                ))
            elif issubclass(group, MenuGroup):
                group.add_item_info(PayloadInfo(
                    entity=resource.entity(),
                    method=resource.default_method()
                ))
            else:
                raise TypeError(f'Что-то не то передал: {type(group)}, ({group})')

        entity = resource.entity()
        if entity in cls._resources:
            raise ValueError(f'Ресурс с такой сущностью уже существует ({entity})')
        cls._resources[entity] = resource

    def find_resource(self, entity: str) -> "Resource":
        return self._inited_resources.get(entity)

    def all_resources(self) -> dict[str, "Resource"]:
        return self._inited_resources

    @classmethod
    def run_app_kwargs(cls):
        return {
            'target': cls.run_target,
            'assets_dir': (Path().parent.absolute() / 'assets').as_posix(),
            'view': None,
            'host': getenv('HOST', None),
            'port': int(getenv('PORT', '8000')),
        }

    @classmethod
    def run_app(cls, **kwargs):
        asyncio.get_event_loop().run_until_complete(cls.on_startup())
        flet_app(**{**cls.run_app_kwargs(), **kwargs})
        asyncio.get_event_loop().run_until_complete(cls.on_shutdown())

    @classmethod
    async def run_target(cls, page: Page):
        page.title = cls.title
        page.padding = 0
        await page.add_async(LoginView(cls))

    @classmethod
    async def on_startup(cls):
        await db_connection.init()
        cls.user_repository = import_string(get_settings().USER_REPOSITORY)
        importlib.import_module('configuration.resources')

    @classmethod
    async def on_shutdown(cls):
        await db_connection.close()

    async def open(self, info: PayloadInfo) -> None:
        if tab := self.tabs_bar.tab_by_info(info=info):
            await self.tabs_bar.set_current_tab(tab)
        else:
            await self.tabs_bar.create_tab(info=info)

    async def notify(
            self,
            content: Control | str,
            status: NotifyStatus = NotifyStatus.INFO,
            action: str = None,
            action_color: str = 'white',
            on_action: Callable[[ControlEvent], Coroutine[Any, Any, None] | None] = None
    ) -> None:
        if isinstance(content, str):
            content = Text(content)
        match status:
            case NotifyStatus.SUCCESS:
                bgcolor = 'green'
            case NotifyStatus.ERROR:
                bgcolor = 'error'
            case NotifyStatus.WARN:
                bgcolor = 'orange'
            case _:
                bgcolor = None
        await self.page.show_snack_bar_async(SnackBar(
            content=content,
            bgcolor=bgcolor,
            show_close_icon=True,
            action=action,
            action_color=action_color,
            on_action=on_action
        ))

    async def add_popup(
            self,
            content: Control,
            title: str = None,
            on_close: Callable[[], Coroutine[..., ..., None]] = None,
            size: tuple[float | int, float | int] = None
    ) -> Popup:
        popup = Popup(
            app=self,
            content=content,
            title=title,
            on_close=on_close,
            size=size
        )
        self.controls.append(popup)
        await self.update_async()
        return popup

    async def close_popup(self, popup: Popup) -> None:
        if popup not in self.controls:
            return
        self.controls.remove(popup)
        await self.update_async()

    async def add_popover(
            self,
            content: Control,
            on_close: Callable[[], Coroutine[..., ..., None]] = None,
    ) -> Popover:
        popover = Popover(
            app=self,
            content=content,
            on_close=on_close,
        )
        self.controls.append(popover)
        await self.update_async()
        return popover

    async def close_popover(self, popover: Popover) -> None:
        if popover not in self.controls:
            return
        self.controls.remove(popover)
        await self.update_async()

    @asynccontextmanager
    async def error_tracker(self):
        try:
            yield
        except Exception as e:
            await UnhandledErrorContainer.open_in_popup(app=self, error=e)
            raise e

    async def logout(self, e=None):
        page = self.page
        await page.clean_async()
        await page.add_async(LoginView(self.__class__))
