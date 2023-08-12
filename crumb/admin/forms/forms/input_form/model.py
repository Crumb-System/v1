from typing import TYPE_CHECKING, Any, Callable, Optional, Type, Coroutine, TypeVar, Generic

from flet import ElevatedButton

from crumb.exceptions import ObjectErrors
from crumb.enums import NotifyStatus
from crumb.orm import BaseModel
from crumb.entities.directories import DirectoryRepository
from crumb.entities.documents import DocumentRepository

from crumb.admin.layout import PayloadInfo
from crumb.admin.forms import Primitive, FormSchema, WidgetSchemaCreator
from crumb.admin.components.errors import ObjectErrorsContainer
from .simple import SimpleInputForm

if TYPE_CHECKING:
    from crumb.admin.resources import Resource
    from crumb.admin.layout import BOX


REP = TypeVar("REP", DirectoryRepository, DocumentRepository)


class ModelInputForm(Generic[REP], SimpleInputForm):

    def __init__(
            self,
            resource: "Resource",
            box: "BOX",
            primitive: Primitive,
            *,
            initial: Optional["BaseModel"] | dict[str, Any] = None,
            on_success: Callable[["ModelInputForm", "BaseModel"], Coroutine[Any, Any, None]] = None,
            on_error: Callable[["ModelInputForm", ObjectErrors], Coroutine[Any, Any, None]] = None,
    ):
        if isinstance(initial, BaseModel):
            self.instance, initial = initial, None
        else:
            self.instance = None
        super().__init__(box=box, initial=initial)
        self.app = self.box.app
        self.resource = resource
        self.primitive = primitive
        self.on_success = on_success or self.on_success_default
        self.on_error = on_error or self.on_error_default

    @property
    def repository(self) -> Type[REP]:
        return self.resource.repository

    @property
    def create(self) -> bool:
        return self.instance is None

    def initial_for(self, name: str):
        if self.create:
            return super().initial_for(name=name)
        else:
            return self.repository.get_instance_value(self.instance, name=name)

    def get_form_schema(self) -> FormSchema:
        return self.schema or self._generate_form_schema()

    def _generate_form_schema(self) -> FormSchema:
        schema = FormSchema()
        widget_creator = self.get_widget_creator()
        for item in self.primitive:
            schema.add_item(widget_creator.from_primitive_item(item))
        return schema

    def get_widget_creator(self):
        return WidgetSchemaCreator(resource=self.resource)

    @staticmethod
    async def on_success_default(form: "ModelInputForm", instance: "BaseModel"):
        if form.create:
            await form.box.close()
            await form.app.open(PayloadInfo(
                entity=form.resource.entity(),
                method='edit',
                query={'pk': instance.pk}
            ))
        else:
            await form.box.reload_content()

    @staticmethod
    async def on_error_default(form: "ModelInputForm", error: ObjectErrors):
        pass

    async def save(self) -> tuple[Optional[BaseModel], bool]:
        if not self.form_is_valid():
            await self.update_async()
            return None, False
        try:
            if self.create:
                return await self.repository().create(self.cleaned_data()), True
            else:
                return await self.repository(instance=self.instance).edit(self.cleaned_data()), False
        except ObjectErrors as err:
            self.set_object_errors(err)
            await self.update_async()
            await self.notify_fix_errors(err)
            await self.on_error(form=self, error=err)
            return None, False

    async def on_click_save(self, e=None):
        async with self.app.error_tracker():
            instance, created = await self.save()
            if instance is None:
                return
            if created:
                await self.app.notify(f'{instance} создан', NotifyStatus.SUCCESS)
                await self.on_success(form=self, instance=instance)
            else:
                await self.app.notify(f'{instance} сохранён', NotifyStatus.SUCCESS)
                await self.on_success(form=self, instance=instance)

    async def notify_fix_errors(self, err: ObjectErrors):
        await self.app.notify(
            'Исправьте ошибки',
            NotifyStatus.ERROR,
            action='Детали',
            on_action=self.show_object_error_details(err)
        )

    def save_btn(self):
        return ElevatedButton(
            'Создать' if self.create else 'Сохранить',
            on_click=self.on_click_save
        )

    def show_object_error_details(self, error: ObjectErrors):
        async def wrapper(e=None):
            await ObjectErrorsContainer.open_in_popup(app=self.app, error=error)
        return wrapper
