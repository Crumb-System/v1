from enum import Enum
from typing import TypeVar, Literal, Any, Optional, Coroutine, Callable, overload, cast, Type

from tortoise import fields
from tortoise.queryset import QuerySet
from tortoise.transactions import in_transaction
from tortoise.exceptions import ValidationError

from crumb.orm.base_model import BaseModel
from crumb.types import MODEL, PK, DATA, SortedData, BackFKData, ValuesListData
from crumb.constants import EMPTY_TUPLE
from crumb.exceptions import ObjectErrors, UnexpectedDataKey, FieldError, NotUnique, \
    FieldRequired, NotFoundFK, RequiredMissed, InvalidType, AnyFieldError, ListFieldError
from .base import ReadRepository
from .values_list_repository import ValuesListRepository


T = TypeVar('T')


class Repository(ReadRepository[MODEL]):

    READ_ONLY_REPOSITORY = False

    def __init__(
            self,
            by: str = None,
            instance: MODEL = None,
            select_related: tuple[str, ...] = EMPTY_TUPLE,
            prefetch_related: tuple[str, ...] = EMPTY_TUPLE,
            annotations: dict[str, ...] = None,
    ):
        super().__init__(
            select_related=select_related,
            prefetch_related=prefetch_related,
            annotations=annotations,
        )
        self.by = by
        self.instance = instance

    async def handle_create(
            self,
            data: DATA,
            extra_data: DATA
    ) -> MODEL:
        return await self.model.create(**data)

    async def get_create_defaults(self, data: DATA, user_defaults: Optional[DATA]) -> DATA:
        return user_defaults or {}

    def raise_if_method_unavailable(self, method: str):
        if self.__class__.READ_ONLY_REPOSITORY and method not in ('list', 'choice'):
            raise Exception(f'{self.__class__} is read_only')
        else:
            getattr(self, f'can_{method}')()

    def can_create(self):
        if self.instance:
            raise Exception('Repository has instance, create new one')

    def can_edit(self):
        if self.instance is None:
            raise Exception('No instance to edit in repository')

    def can_delete(self):
        if self.instance is None:
            raise Exception('No instance to delete in repository')

    def can_delete_many(self):
        return True

    async def get_values_list(self, name: str = 'values_list'):
        repository_cls = self.repository_of(name)
        assert issubclass(repository_cls, ValuesListRepository)
        return await repository_cls(owner_instance=self.instance).get_records()

    async def create(
            self,
            data: DATA,
            *,
            defaults: Optional[DATA] = None,
            is_root: bool = True,
            run_in_transaction: Optional[bool] = None,
            validate: Optional[bool] = None,
    ) -> MODEL:
        """
        :param data: Данные для вставки в БД, которые соответствуют её структуре.
                     После передачи в функцию данные никак не изменяются.
        :param defaults: Данные, которые вставляются по умолчанию БЕЗ ПРОВЕРКИ. Используется, например, чтобы
                         установить ссылку на ntreobq объект, создавая back_o2o или back_fk
        :param is_root: Явно указывает находимся ли мы в корне или функция create вызвана другим Repository.create
        :param run_in_transaction: По умолчанию равно параметру is_root.
                                   Указывает нужно ли помещать вызов функции в транзакцию. Если функция уже находится в
                                   транзации, то новый контекст транзакции сломает отлов ошибки и собъет connection.
        :param validate: По умолчанию равно параметру is_root.
                         Стоит вручную передавать False, если передаются валидированные данные. Автоматически False
                         передается вместе с is_root, когда Repository.create вызывается из другой функции.
        """
        self.raise_if_method_unavailable('create')

        validate = is_root if validate is None else validate
        run_in_transaction = is_root if run_in_transaction is None else run_in_transaction

        if validate:
            await self.validate(data)

        async def get_new_instance() -> MODEL:
            direct_related = {}
            sorted_data: SortedData = self.sort_data_by_field_types(data)

            for t in ('o2o', 'fk'):
                t: Literal["o2o", "fk"]
                for field_name, value in getattr(sorted_data, t).items():
                    direct_related[field_name] = await self.repository_of(field_name)(
                        by=self.get_reverse_name(field_name)
                    ).create(value, is_root=False)

            for t in ('o2o_pk', 'fk_pk'):
                t: Literal["o2o_pk", "fk_pk"]
                for field_name, value in getattr(sorted_data, t).items():
                    # при валидации мы убедились, что запись в бд есть, поэтому просто подвязываем по первичному ключу
                    direct_related[field_name] = value

            result_defaults = await self.get_create_defaults(data, defaults)
            instance = await self.handle_create(
                data={**result_defaults, **sorted_data.db_field, **direct_related},
                extra_data=sorted_data.extra
            )

            for field_name, value in sorted_data.back_o2o.items():
                relation_field = self.get_field_instance(field_name).relation_source_field  # type: ignore
                await self.repository_of(field_name)(by=relation_field)\
                    .create(value, defaults={relation_field: instance.pk}, is_root=False)

            for field_name, bfk_data in sorted_data.back_fk.items():
                relation_field = self.get_field_instance(field_name).relation_source_field  # type: ignore
                remote_repository_cls = self.repository_of(field_name)
                if issubclass(remote_repository_cls, ValuesListRepository):
                    if bfk_data['values']:
                        await remote_repository_cls(owner_instance=instance).create_list(bfk_data)
                    continue
                remote_repository_cls = cast(Type[Repository], remote_repository_cls)
                for value in bfk_data:
                    await remote_repository_cls(by=relation_field)\
                        .create(value, defaults={relation_field: instance.pk}, is_root=False)

            self.instance = instance
            return instance

        if run_in_transaction:
            async with in_transaction():
                return await self.get_one((await get_new_instance()).pk)
        else:
            return await get_new_instance()

    async def handle_edit(
            self,
            data: DATA,
            extra_data: DATA
    ):
        self.instance.update_from_dict(data)
        await self.instance.save(force_update=True)

    async def edit(
            self,
            data: DATA,
            *,
            defaults: Optional[DATA] = None,
            is_root: bool = True,
            run_in_transaction: Optional[bool] = None,
            validate: Optional[bool] = None,
    ) -> MODEL:
        """
        :param data: Данные для вставки в БД, которые соответствуют её структуре.
                     После передачи в функцию данные никак не изменяются.
        :param defaults: Данные, которые вставляются по умолчанию БЕЗ ПРОВЕРКИ. Используется, например, чтобы
                         установить ссылку на ntreobq объект, создавая back_o2o или back_fk
        :param is_root: Явно указывает находимся ли мы в корне или функция create вызвана другим Repository.create
        :param run_in_transaction: По умолчанию равно параметру is_root.
                                   Указывает нужно ли помещать вызов функции в транзакцию. Если функция уже находится в
                                   транзации, то новый контекст транзакции сломает отлов ошибки и собъет connection.
        :param validate: По умолчанию равно параметру is_root.
                         Стоит вручную передавать False, если передаются валидированные данные. Автоматически False
                         передается вместе с is_root, когда Repository.create вызывается из другой функции.
        """
        self.raise_if_method_unavailable('edit')

        validate = is_root if validate is None else validate
        run_in_transaction = is_root if run_in_transaction is None else run_in_transaction

        if validate:
            await self.validate(data)
        # TODO: clean_edit_data for history

        async def get_updated_instance() -> MODEL:
            direct_related = {}
            sorted_data: SortedData = self.sort_data_by_field_types(data)

            for t in ('o2o', 'fk'):
                for field_name, value in getattr(sorted_data, t).items():
                    rel_instance = await self.get_relational(field_name)
                    if rel_instance:
                        await self.repository_of(field_name)(
                            by=self.get_reverse_name(field_name),
                            instance=rel_instance
                        ).edit(value, is_root=False)
                    else:
                        direct_related[field_name] = await self.repository_of(field_name)(
                            by=self.get_reverse_name(field_name)
                        ).create(value, is_root=False)

            for t in ('o2o_pk', 'fk_pk'):
                for field_name, value in getattr(sorted_data, t).items():
                    direct_related[field_name] = value

            await self.handle_edit(
                data={**(defaults or {}), **sorted_data.db_field, **direct_related},
                extra_data=sorted_data.extra
            )

            for field_name, value in sorted_data.back_o2o.items():
                rel_instance = await self.get_relational(field_name)
                relation_field = self.get_field_instance(field_name).relation_source_field  # type: ignore
                if rel_instance:
                    await self.repository_of(field_name)(
                        by=relation_field,
                        instance=rel_instance
                    ).edit(value, is_root=False)
                else:
                    await self.repository_of(field_name)(
                        by=relation_field
                    ).create(value, defaults={relation_field: self.instance.pk}, is_root=False)

            for field_name, bfk_data in sorted_data.back_fk.items():
                remote_repository_cls = self.repository_of(field_name)
                if issubclass(remote_repository_cls, ValuesListRepository):
                    await remote_repository_cls(owner_instance=self.instance).edit_list(new_data=bfk_data)
                    continue
                remote_repository_cls = cast(Type[Repository], remote_repository_cls)
                reverse_name = self.get_reverse_name(field_name)
                relation_field = self.get_field_instance(field_name).relation_source_field  # type: ignore
                rel_instances_map = await self.get_relational_list(field_name, in_map=True)
                for value in bfk_data:
                    if 'pk' in value:
                        rel_instance = rel_instances_map.pop(value['pk'])
                        await remote_repository_cls(by=reverse_name, instance=rel_instance)\
                            .edit(
                                {k: v for k, v in value.items() if k != 'pk'},
                                is_root=False
                            )
                    else:
                        await remote_repository_cls(by=reverse_name).create(
                            value,
                            defaults={relation_field: self.instance.pk},
                            is_root=False
                        )
                if rel_instances_map:
                    await remote_repository_cls(by=reverse_name).delete_many([v.pk for v in rel_instances_map.values()])

            return self.instance

        if run_in_transaction:
            async with in_transaction():
                return await self.get_one((await get_updated_instance()).pk)
        else:
            return await get_updated_instance()

    async def delete_many(self, item_pk_list: list[PK]) -> int:
        self.raise_if_method_unavailable('delete_many')
        return await self._delete_many(item_pk_list)

    async def _delete_many(self, item_pk_list: list[PK]) -> int:
        raise NotImplementedError('Для этой модели не определено множественное удаление')

    async def delete(self) -> None:
        self.raise_if_method_unavailable('delete')
        await self._delete()

    async def _delete(self) -> None:
        raise NotImplementedError('Для этой модели не определено удаление')

    async def check_fk_exists(self, field_name: str, item_pk: PK) -> BaseModel:
        field_type, field = self.get_field_type_and_instance(field_name)

        if field_type.is_no_pk_relation():
            related_field = cast(fields.relational.RelationalField, field)
        elif field_type.is_pk_relation():
            related_field = cast(fields.relational.ForeignKeyFieldInstance, field.reference)
        else:
            raise Exception(f'{self.model}.{field_name} не относится к o2o, o2o_pk, fk, fk_pk, back_o2o, back_fk')
        related_instance = await related_field.related_model.get_or_none(pk=item_pk)
        if related_instance is None:
            raise NotFoundFK
        return related_instance

    async def check_unique(
            self,
            field_name: str,
            value: Any,
            data: DATA,
    ) -> None:
        if self.instance and getattr(self.instance, field_name) == value:
            return
        if await self.model.exists(**{field_name: value}):
            raise NotUnique

    async def check_unique_together(
            self,
            data: DATA,
    ) -> None:
        """Недоделано"""
        raise NotImplementedError
        # errors = ObjectErrors()
        # for combo in self.opts().unique_together:
        #     values = {}
        # if instance:
        # for field_name in combo:
        # field = self.get_field_instance(field_name)
        # :) посмотри какие именно значения добавляются в unique_together, если пишешь туда o2o и fk
        # if await self.model.exists(**values):
        #     errors.add('__root__', NotUniqueTogether(combo))
        # if errors:
        #     raise errors

    @classmethod
    def sort_data_by_field_types(cls, data: DATA) -> SortedData:
        _all_fields = cls.describe().all
        sorted_data = SortedData()

        for key, value in data.items():
            field_type = _all_fields.get(key)
            if field_type is None:
                if key in cls.extra_allowed:
                    sorted_data.extra[key] = value
                    continue
                raise UnexpectedDataKey(f'`{key}` не представлен в `{cls.model}`')
            if field_type.is_hidden():
                raise UnexpectedDataKey(f'`{key}` скрыт в `{cls.model}`')
            field_type_value = cast(str, field_type.value)
            if field_type_value in sorted_data.__dict__:
                getattr(sorted_data, field_type_value)[key] = value
            else:
                sorted_data.db_field[key] = value
        return sorted_data

    async def validate(self, data: DATA) -> None:
        errors = ObjectErrors()

        required, pairs = self.required_and_pairs()
        required = required if self.instance is None else {}
        if self.by and self.by in required:
            related = required.pop(self.by)
            del required[related]

        sorted_data = self.sort_data_by_field_types(data)

        for t in SortedData.__annotations__.keys():
            for name, value in getattr(sorted_data, t).items():
                if name in required:
                    related = required[name]
                    del required[name]
                    if related:
                        del required[related]
                if name in pairs:
                    if pairs[name] not in pairs:
                        raise Exception(f'{name} и {pairs[name]} были переданы одновременно')
                    del pairs[name]
                try:
                    await self.validate_field(
                        name, value, data, default_validator=getattr(self, f'validate_{t}')
                    )
                except (FieldError, ObjectErrors) as e:
                    errors.add(name, e)

        for name, related in required.items():
            errors.add('__root__', RequiredMissed(name, related))
        if errors:
            raise errors

    def validate_field(
            self,
            field_name: str,
            value: T,
            data: DATA,
            default_validator: Callable[[str, T, DATA], Coroutine[Any, Any, None]]
    ) -> Optional[Coroutine[Any, Any, None]]:
        validator = getattr(self, f'_validate_{field_name}', None)
        if validator:
            return validator(value, data)
        return default_validator(field_name, value, data)

    async def get_relational(self, field_name: str) -> Optional[BaseModel]:
        rel_instance = getattr(self.instance, field_name)
        if isinstance(rel_instance, QuerySet):
            await self.instance.fetch_related(field_name)
            rel_instance = getattr(self.instance, field_name)
        return rel_instance

    @overload
    async def get_relational_list(self, field_name: str, in_map: bool) -> dict[PK, BaseModel]:
        ...

    @overload
    async def get_relational_list(self, field_name: str) -> list[BaseModel]:
        ...

    async def get_relational_list(
            self,
            field_name: str,
            in_map: bool = False,
    ) -> list[BaseModel] | dict[PK, BaseModel]:
        rel_instances: list[BaseModel] = getattr(self.instance, field_name)
        if isinstance(rel_instances, QuerySet):
            await self.instance.fetch_related(field_name)
            rel_instances = getattr(self.instance, field_name)
        if in_map:
            return {i.pk: i for i in rel_instances}
        return rel_instances

    async def validate_relational(
            self,
            field_name: str,
            value: DATA,
            data: DATA,
    ):
        await self.repository_of(field_name)(
            by=self.get_reverse_name(field_name),
            instance=await self.get_relational(field_name) if self.instance else None
        ).validate(value)

    async def validate_o2o(
            self,
            field_name: str,
            value: DATA,
            data: DATA,
    ) -> None:
        if not isinstance(data, dict):
            raise InvalidType(f'o2o `{self.model}.{field_name}` data must be dict, not {type(value)} ({value})')
        await self.validate_relational(field_name, value, data)

    async def validate_o2o_pk(
            self,
            field_name: str,
            value: PK,
            data: DATA,
    ) -> Optional[BaseModel]:
        field = self.get_field_instance(field_name)

        if value is None:
            if not field.null:
                raise FieldRequired
            return

        if not isinstance(value, field.field_type):  # передали неправильный тип pk
            raise InvalidType(
                f'o2o_pk `{self.model}.{field_name}` data must be int, not {type(value)} ({value})'
            )

        value: PK
        await self.check_unique(field_name, value, data)
        return await self.check_fk_exists(field_name, value)

    async def validate_fk(
            self,
            field_name: str,
            value: DATA,
            data: DATA,
    ) -> None:
        if not isinstance(value, dict):
            raise InvalidType(f'fk `{self.model}.{field_name}` data must be dict, not {type(value)} ({value})')
        await self.validate_relational(field_name, value, data)

    async def validate_fk_pk(
            self,
            field_name: str,
            value: PK,
            data: DATA,
    ) -> Optional[BaseModel]:
        field = self.get_field_instance(field_name)

        if value is None:
            if not field.null:
                raise FieldRequired
            return

        if not isinstance(value, field.field_type):  # передали правильный тип pk
            raise InvalidType(
                f'fk_pk `{self.model}.{field_name}` data must be {PK}, not {type(value)} ({value})'
            )
        value: PK
        return await self.check_fk_exists(field_name, value)

    async def validate_back_o2o(
            self,
            field_name: str,
            value: DATA,
            data: DATA,
    ) -> None:
        if not isinstance(value, dict):
            raise InvalidType(f'back_o2o `{self.model}.{field_name}` data must be dict, not {type(value)} ({value})')
        await self.validate_relational(field_name, value, data)

    async def validate_back_fk(
            self,
            field_name: str,
            value: BackFKData | ValuesListData,
            data: DATA,
    ) -> None:
        values = value  # alias

        remote_repository_cls = self.repository_of(field_name)
        if issubclass(remote_repository_cls, ValuesListRepository):
            if values['values']:
                remote_repository_cls = cast(Type[ValuesListRepository], remote_repository_cls)
                await remote_repository_cls(owner_instance=self.instance).validate_list(values)
            return
        list_errors = ListFieldError()

        if not isinstance(values, list) and all(isinstance(v, dict) for v in values):
            raise InvalidType(
                f'back_fk `{self.model}.{field_name}` `data-add` must be list[dict], '
                f'not {type(values)} ({values})'
            )

        if self.instance is None:
            if any(['pk' in v for v in values]):
                raise ValueError(f'pk может быть передан только если объект изменяется, а не создается')
            rel_instance_map = {}
        else:
            rel_instance_map = await self.get_relational_list(field_name, in_map=True)

        remote_repository_cls = cast(Type[Repository], remote_repository_cls)
        reverse_name = self.get_reverse_name(field_name)
        for i, val in enumerate(values):
            rel_instance = None
            if 'pk' in val:
                rel_instance = rel_instance_map.get(val['pk'])
                if rel_instance is None:
                    list_errors.append(i, ObjectErrors().add('__root__', NotFoundFK))
                    continue
                val = {k: v for k, v in val.items() if k != 'pk'}
            try:
                await remote_repository_cls(
                    by=reverse_name,
                    instance=rel_instance
                ).validate(val)
            except ObjectErrors as err:
                list_errors.append(i, err)

        if list_errors:
            raise list_errors

    async def validate_db_field(
            self,
            field_name: str,
            value: Any,
            data: DATA,
    ) -> None:
        field = self.get_field_instance(field_name)
        if value is None and not field.null:
            raise FieldRequired
        if field.generated:
            raise UnexpectedDataKey(f'{field_name} is generated in {self.__class__}')
        if value is not None and not isinstance(value, field.field_type):
            raise InvalidType(f'{self.model}.{field_name} data must be instance of {field.field_type}, '
                              f'not {type(value)} ({value})')
        if field.unique:
            await self.check_unique(field_name, value, data)
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

    async def validate_extra(
            self,
            field_name: str,
            value: Any,
            data: DATA,
    ) -> None:
        pass
