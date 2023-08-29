from enum import Enum
from typing import Any, Type, TYPE_CHECKING, Optional, Generic

from tortoise import fields
from tortoise.exceptions import ValidationError
from tortoise.functions import Max

from .base import BaseRepository
from ..constants import UndefinedValue
from ..enums import FieldTypes
from ..orm import BaseModel
from ..types import LIST_VALUE_MODEL, MODEL, RepositoryDescription, ValuesListData, PK, DATA
from ..exceptions import ListFieldError, UnexpectedDataKey, AnyFieldError, InvalidType, FieldRequired, FieldError, \
    ObjectErrors, NotFoundFK

if TYPE_CHECKING:
    from .repository import Repository


class ValuesListRepository(Generic[LIST_VALUE_MODEL, MODEL], BaseRepository[LIST_VALUE_MODEL]):

    hidden_fields = {'id', 'owner', 'owner_id'}

    def __init__(self, owner_instance: Optional[MODEL] = None):
        self.owner_instance = owner_instance

    async def get_records(self) -> list[LIST_VALUE_MODEL]:
        return await self.model.filter(owner=self.owner_instance).order_by('ordering')

    @classmethod
    def get_row_data(cls, head: tuple[str, ...], value: tuple[str, ...]) -> DATA:
        return {k: v for j, k in enumerate(head) if (v := value[j]) is not UndefinedValue}

    async def create_list(self, data: ValuesListData, start_ordering: int = 1):
        assert self.owner_instance
        assert start_ordering >= 1
        records: list[LIST_VALUE_MODEL] = []
        head = data['head']
        values = data['values']
        for i, value in enumerate(values, start=start_ordering):
            record_data = self.get_row_data(head=head, value=value)
            record_data['ordering'] = i
            record = self.model(owner=self.owner_instance, **record_data)
            record.set_pk()
            records.append(record)
        await self.model.bulk_create(records, batch_size=100)

    async def add(self, data: ValuesListData):
        assert self.owner_instance
        result = await self.model\
            .filter(owner=self.owner_instance)\
            .annotate(last_number=Max('ordering'))\
            .first()\
            .values('last_number')
        last_number = result.get('last_number') or 0
        await self.create_list(data=data, start_ordering=last_number + 1)

    async def append(self, row: DATA):
        await self.add({'head': tuple(k for k in row.keys()), 'values': [tuple(v for v in row.values())]})

    async def edit_list(self, new_data: ValuesListData):
        assert self.owner_instance
        await self.clear()
        if new_data['values']:
            await self.create_list(data=new_data)

    async def clear(self):
        assert self.owner_instance
        await self.model.filter(owner=self.owner_instance).delete()

    async def validate_list(self, data: ValuesListData, check_required: bool = True):
        list_error = ListFieldError()
        required, pairs = self.required_and_pairs()
        head = data['head']
        values = data['values']
        for i, field_name in enumerate(head):
            field_is_required = field_name in required
            if field_is_required:
                related = required[field_name]
                del required[field_name]
                if related:
                    del required[related]

            field_type = self.get_field_type(field_name)
            if field_type.is_db_field():
                await self.validate_db_field_list(
                    field_name=field_name,
                    value_list=[v[i] for v in values],
                    data=data,
                    is_required=field_is_required,
                    list_error=list_error
                )
            elif field_type.is_hidden():
                raise UnexpectedDataKey(f'{field_name} in hidden in {self.__class__}')
            elif field_type == FieldTypes.FK_PK:
                await self.validate_fk_pk_list(
                    field_name=field_name,
                    value_list=[v[i] for v in values],
                    data=data,
                    is_required=field_is_required,
                    list_error=list_error
                )
            elif field_name in self.extra_allowed:
                await self.validate_extra_list(
                    field_name=field_name,
                    value_list=[v[i] for v in values],
                    data=data,
                    is_required=field_is_required,
                    list_error=list_error
                )

        if required and check_required:
            raise ValueError(required)

        if list_error:
            raise list_error

    async def validate_db_field_list(
            self,
            field_name: str,
            value_list: list[...],
            data: ValuesListData,
            is_required: bool,
            list_error: ListFieldError
    ):
        field = self.get_field_instance(field_name)
        if field.generated:
            raise UnexpectedDataKey(f'{field_name} is generated for {self.__class__}')
        if field.unique:
            raise Exception('values_list field can`t be unique')
        validator = getattr(self, f'_validate_{field.model_field_name}', self.validate_db_field)
        head, values = data['head'], data['values']
        for i, value in enumerate(value_list):
            row = self.get_row_data(head=head, value=values[i])
            try:
                await validator(field=field, value=value, is_required=is_required, row=row)
            except FieldError as e:
                self.set_object_error(list_error=list_error, index=i, field_name=field_name, error=e)

    async def validate_db_field(
            self,
            field: fields.Field,
            value: Any,
            is_required: bool,
            row: DATA
    ):
        if value is None and not field.null:
            raise FieldRequired
        if is_required and value is UndefinedValue:
            raise FieldRequired
        if not isinstance(value, field.field_type):
            raise InvalidType(f'{self.model}.{field.model_field_name} data must be instance of {field.field_type}, '
                              f'not {type(value)} ({value})')
        # позаимствовал кусок из field.validate(value) за исключением последней строки
        for v in field.validators:
            if field.null and value is None:
                continue
            try:
                if isinstance(value, Enum):
                    v(value.value)
                else:
                    v(value)
            except ValidationError as exc:
                raise AnyFieldError('invalid', str(exc))

    async def validate_fk_pk_list(
            self,
            field_name: str,
            value_list: list[PK],
            data: ValuesListData,
            is_required: bool,
            list_error: ListFieldError
    ):
        remote_repository: "Repository" = self.repository_of(field_name)()  # type: ignore
        instances_map: dict[PK, BaseModel] = {
            instance.pk: instance
            for instance in await remote_repository.get_many(value_list)
        }
        for i, value in enumerate(value_list):
            if value not in instances_map:
                self.set_object_error(
                    list_error=list_error,
                    index=i,
                    field_name=field_name,
                    error=NotFoundFK
                )

    def set_object_error(
            self,
            list_error: ListFieldError,
            index: int,
            field_name: str,
            error: FieldError | Type[FieldError] | ObjectErrors
    ):
        if index in list_error:
            object_errors = list_error[index]
        else:
            object_errors = ObjectErrors()
            list_error.append(index, object_errors)
        object_errors.add(field=field_name, error=error)

    async def validate_extra_list(
            self,
            field_name: str,
            value_list: list[PK],
            data: ValuesListData,
            is_required: bool,
            list_error: ListFieldError
    ):
        pass

    @classmethod
    def _calc_description(cls) -> RepositoryDescription:
        description = super()._calc_description()
        assert \
            all(
                v.is_db_field()
                or v.is_hidden()
                or v in (FieldTypes.FK_PK, FieldTypes.FK)
                for v in description.all.values()
            ), description.all
        return description
