from typing import Callable, Optional, Coroutine, TYPE_CHECKING, Type, TypeVar, Any

from flet import Control

from crumb.types import PK
from crumb.exceptions import ObjectErrors
from crumb.constants import EMPTY_TUPLE
from crumb.entities.directories import DirectoryRepository
from crumb.entities.documents import DocumentRepository
from .base import Resource
from ..forms import ListForm, ChoiceForm, ModelInputForm, Primitive

if TYPE_CHECKING:
    from crumb.admin.layout import BOX
    from crumb.orm import BaseModel


REP = TypeVar('REP', DirectoryRepository, DocumentRepository)


class CrudResource(Resource[REP]):

    list_form = ListForm
    choice_form = ChoiceForm

    list_form_primitive: Primitive = None
    choice_form_primitive: Primitive = None

    model_form: Type[ModelInputForm[REP]]
    form_primitive: Primitive = None
    create_model_form: Optional[Type[ModelInputForm[REP]]] = None
    create_form_primitive: Primitive = None
    edit_model_form: Optional[Type[ModelInputForm[REP]]] = None
    edit_form_primitive: Primitive = None

    list_base_sort: tuple[str, ...] = EMPTY_TUPLE
    common_select_related: tuple[str, ...] = EMPTY_TUPLE
    common_prefetch_related: tuple[str, ...] = EMPTY_TUPLE
    list_select_related: tuple[str, ...] = EMPTY_TUPLE
    list_prefetch_related: tuple[str, ...] = EMPTY_TUPLE
    choice_select_related: tuple[str, ...] = EMPTY_TUPLE
    choice_prefetch_related: tuple[str, ...] = EMPTY_TUPLE
    edit_select_related: tuple[str, ...] = EMPTY_TUPLE
    edit_prefetch_related: tuple[str, ...] = EMPTY_TUPLE

    async def get_list_primitive(self):
        return self.list_form_primitive

    async def get_list_select_related(self) -> tuple[str, ...]:
        return *self.common_select_related, *self.list_select_related

    async def get_list_prefetch_related(self) -> tuple[str, ...]:
        return *self.common_prefetch_related, *self.list_prefetch_related

    async def get_list_base_sort(self) -> tuple[str, ...]:
        return self.list_base_sort

    async def get_choice_primitive(self):
        return self.choice_form_primitive or self.list_form_primitive

    async def get_choice_select_related(self) -> tuple[str, ...]:
        return *self.common_select_related, *self.choice_select_related

    async def get_choice_prefetch_related(self) -> tuple[str, ...]:
        return *self.common_prefetch_related, *self.choice_prefetch_related

    async def get_create_form_primitive(self):
        return self.create_form_primitive or self.form_primitive

    async def get_create_model_form(self):
        return self.create_model_form or self.model_form

    async def get_edit_form_primitive(self):
        return self.edit_form_primitive or self.form_primitive

    async def get_edit_model_form(self):
        return self.edit_model_form or self.model_form

    async def get_edit_select_related(self) -> tuple[str, ...]:
        return *self.common_select_related, *self.edit_select_related

    async def get_edit_prefetch_related(self) -> tuple[str, ...]:
        return *self.common_prefetch_related, *self.edit_prefetch_related

    async def get_list_form(
            self,
            box: "BOX",
            primitive: "Primitive" = None,
    ) -> ListForm:
        view = self.list_form(
            box=box,
            primitive=primitive or await self.get_list_primitive(),
            select_related=await self.get_list_select_related(),
            prefetch_related=await self.get_list_prefetch_related(),
            sort=await self.get_list_base_sort()
        )
        return self.with_tab_title(view, 'list')

    async def get_choice_view(
            self,
            box: "BOX",
            make_choice: Callable[[Optional["BaseModel"]], Coroutine[..., ..., None]],
            primitive: "Primitive" = None,
    ) -> ChoiceForm:
        view = self.choice_form(
            box=box,
            primitive=primitive or await self.get_choice_primitive(),
            make_choice=make_choice,
            select_related=await self.get_list_select_related(),
            prefetch_related=await self.get_list_prefetch_related(),
            sort=await self.get_list_base_sort()
        )
        return self.with_tab_title(view, 'choice')

    async def get_create_form(
            self,
            box: "BOX",
            on_success: Callable[[ModelInputForm[REP], "BaseModel"], Coroutine[..., ..., None]] = None,
            on_error: Callable[[ModelInputForm[REP], "ObjectErrors"], Coroutine[..., ..., None]] = None,
            initial: dict[str, Any] = None
    ) -> ModelInputForm[REP]:
        model_form = self.create_model_form or self.model_form
        form = model_form(
            resource=self,
            box=box,
            initial=initial,
            primitive=await self.get_create_form_primitive(),
            on_success=on_success,
            on_error=on_error,
        )
        return self.with_tab_title(form, 'create')

    async def get_edit_form(
            self,
            box: "BOX",
            pk: PK,
            on_success: Callable[[ModelInputForm[REP], "BaseModel"], Coroutine[..., ..., None]] = None,
            on_error: Callable[[ModelInputForm[REP], "ObjectErrors"], Coroutine[..., ..., None]] = None,
    ) -> ModelInputForm[REP] | Control:
        instance = await self.repository(
            select_related=await self.get_edit_select_related(),
            prefetch_related=await self.get_edit_prefetch_related(),
        ).get_one(pk)
        primitive = self.edit_form_primitive or self.form_primitive
        model_form = self.edit_model_form or self.model_form
        form = model_form(
            resource=self,
            box=box,
            primitive=primitive,
            initial=instance,
            on_success=on_success,
            on_error=on_error,
        )
        return self.with_tab_title(form, 'edit', instance=instance)

    @classmethod
    def default_method(cls) -> str:
        return 'list'

    def _methods(self) -> dict[str, Callable[["BOX", ...], Control | Coroutine[..., ..., Control]]]:
        if self.repository.READ_ONLY_REPOSITORY:
            return {
                'list': self.get_list_form,
                'choice': self.get_choice_view,
            }
        return {
            'list': self.get_list_form,
            'choice': self.get_choice_view,
            'create': self.get_create_form,
            'edit': self.get_edit_form,
        }

    def _tab_title_list(self) -> str:
        return self.translation.list()

    def _tab_title_choice(self) -> str:
        return self.translation.choice()

    def _tab_title_create(self) -> str:
        return self.translation.create()

    def _tab_title_edit(self, instance: "BaseModel") -> str:
        return self.translation.edit(instance=instance)

    def _compare_tab_list(self, query1: dict[str, ...], query2: dict[str, ...]) -> bool:
        return True

    def _compare_tab_choice(self, query1: dict[str, ...], query2: dict[str, ...]) -> bool:
        return False

    def _compare_tab_create(self, query1: dict[str, ...], query2: dict[str, ...]) -> bool:
        return True

    def _compare_tab_edit(self, query1: dict[str, ...], query2: dict[str, ...]) -> bool:
        return query1['pk'] == query2['pk']
