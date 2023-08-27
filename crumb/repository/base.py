from typing import Generic, Type, cast, Optional, TypeVar, overload

from tortoise import fields
from tortoise.models import MetaInfo
from tortoise.queryset import QuerySet, Q
from tortoise.transactions import in_transaction

from crumb.constants import UndefinedValue, EMPTY_TUPLE
from crumb.enums import FieldTypes
from crumb.exceptions import ItemNotFound
from crumb.filters import Filter
from crumb.maps import field_instance_to_type
from crumb.orm import BaseModel
from crumb.types import MODEL, PK, RepositoryDescription

descriptions = {}
REPOSITORY = TypeVar('REPOSITORY', bound=Type["BaseRepository"])


class BaseRepository(Generic[MODEL]):
    model: Type[MODEL]
    _REPOSITORY_NAME: str = '__default__'

    hidden_fields: set[str] = set()  # заменить на mutable?
    extra_allowed: dict[str, FieldTypes | tuple[FieldTypes, dict[str, ...]]] = dict()  # заменить на mutable?
    calculated: dict[str, FieldTypes | tuple[FieldTypes, dict[str, ...]]] = dict()  # заменить на mutable?
    related_repositories: dict[str, str] = dict()  # заменить на mutable?

    @classmethod
    def opts(cls) -> MetaInfo:
        return cls.model._meta

    @property
    def pk_field_type(self) -> Type[PK]:
        return self.opts().pk.field_type  # type: ignore

    @property
    def pk_attr(self) -> str:
        return self.opts().pk_attr

    @classmethod
    def _calc_description(cls) -> RepositoryDescription:
        description = RepositoryDescription()
        opts = cls.opts()

        def add_to_hidden(_name: str, _field: fields.Field):
            description.hidden[_name] = _field
            description.all[_name] = FieldTypes.HIDDEN

        for name in opts.o2o_fields:
            field = cast(fields.relational.OneToOneFieldInstance, opts.fields_map[name])
            if name in cls.hidden_fields:
                add_to_hidden(name, field)
            else:
                description.o2o[name] = field
                description.all[name] = FieldTypes.O2O
            source_field = field.source_field
            if source_field in cls.hidden_fields:
                add_to_hidden(name, field)
            else:
                description.o2o_pk[source_field] = opts.fields_map[source_field]
                description.all[source_field] = FieldTypes.O2O_PK

        for name in opts.fk_fields:
            field = cast(fields.relational.ForeignKeyFieldInstance, opts.fields_map[name])
            if name in cls.hidden_fields:
                add_to_hidden(name, field)
            else:
                description.fk[name] = field
                description.all[name] = FieldTypes.FK
            source_field = field.source_field
            if source_field in cls.hidden_fields:
                add_to_hidden(name, field)
            else:
                description.fk_pk[source_field] = opts.fields_map[source_field]
                description.all[source_field] = FieldTypes.FK_PK

        for name in opts.backward_o2o_fields:
            field = cast(fields.relational.BackwardOneToOneRelation, opts.fields_map[name])
            if name in cls.hidden_fields:
                add_to_hidden(name, field)
            else:
                description.back_o2o[name] = field
                description.all[name] = FieldTypes.BACK_O2O

        for name in opts.backward_fk_fields:
            field = cast(fields.relational.BackwardFKRelation, opts.fields_map[name])
            if name in cls.hidden_fields:
                add_to_hidden(name, field)
            description.back_fk[name] = field
            description.all[name] = FieldTypes.BACK_FK

        if opts.m2m_fields:
            raise Exception('M2M запрещены здравым смыслом')

        for name in opts.db_fields:
            # если не o2o_pk/fk_pk
            if name not in description.all:
                field = opts.fields_map[name]
                if name in cls.hidden_fields:
                    add_to_hidden(name, field)
                else:
                    description.db_field[name] = field
                    description.all[name] = field_instance_to_type[field.__class__]
        return description

    @classmethod
    def describe(cls) -> RepositoryDescription:
        description = descriptions.get(cls)
        if description is None:
            descriptions[cls] = description = cls._calc_description()
        return description

    @classmethod
    def get_field_type(cls, field_name: str) -> FieldTypes:
        return cls.describe().all[field_name]

    @classmethod
    def get_field_instance(cls, field_name: str) -> fields.Field:
        _, field_instance = cls.get_field_type_and_instance(field_name)
        return field_instance

    @classmethod
    def get_field_type_and_instance(cls, field_name: str) -> tuple[FieldTypes, fields.Field]:
        field_type = cls.get_field_type(field_name)
        field_type_value = cast(str, field_type.value)
        if field_type_value in RepositoryDescription.__annotations__:
            return field_type, getattr(cls.describe(), field_type_value)[field_name]
        return field_type, cls.describe().db_field[field_name]

    @classmethod
    def field_is_required(cls, field: fields.Field | str) -> bool:
        if isinstance(field, str):
            field = cls.get_field_instance(field)
        if cls.get_field_type(field.model_field_name).is_hidden():
            return False
        if isinstance(field, (fields.DatetimeField, fields.TimeField)) and (field.auto_now or field.auto_now_add):
            return False
        if field.required:
            return True
        return False

    @classmethod
    def required_and_pairs(cls) -> tuple[dict[str, Optional[str]], dict[str, str]]:
        """
        Возвращает заранее просчитанную копию обязательных полей и пар o2o с o2o_pk и fk с fk_pk
        Ключ - это поле, значение - это связанное поле. {"name": None, "user_id": "user", "user": "user_id"}
        У pairs только пары. Это нужно, чтобы определять, например, что передали одновременно и user, и user_id
        """
        if not hasattr(cls, '__required_and_pairs'):
            describe = cls.describe()
            required = {}
            pairs = {}
            for name, field in describe.db_field.items():
                if cls.field_is_required(field):
                    required[name] = None
            for name, field in {**describe.o2o, **describe.fk}.items():
                if cls.field_is_required(field):
                    required[name] = field.source_field
                    pairs[name] = field.source_field
            for name, field in {**describe.o2o_pk, **describe.fk_pk}.items():
                if cls.field_is_required(field):
                    required[name] = field.reference.model_field_name
                    pairs[name] = field.reference.model_field_name
            setattr(cls, '__required_and_pairs', (required, pairs))
        required, pairs = getattr(cls, '__required_and_pairs')
        return {**required}, {**pairs}

    @classmethod
    def get_related_repositories(cls) -> dict[str, str]:
        return cls.related_repositories

    @classmethod
    def repository_of(cls, field_name: str) -> Type[REPOSITORY]:
        field_type, field = cls.get_field_type_and_instance(field_name)
        if field_type.is_no_pk_relation():
            reference = cast(fields.relational.RelationalField, field)
        elif field_type.is_pk_relation():
            reference = cast(fields.relational.RelationalField, field.reference)
        else:
            raise ValueError(
                f'Поле {cls.model}.{field_name} с типом {cls.get_field_type(field_name)} не может иметь репозиторий'
            )
        related_model: BaseModel = reference.related_model
        repo_name = cls.get_related_repositories().get(reference.model_field_name, '__default__')
        repo = related_model.REPOSITORIES.get(repo_name)
        if repo is None:
            raise ValueError(
                f'У поля {cls.model}.{field_name} ({related_model}) нет репозитория {repo_name}'
            )
        return repo

    @classmethod
    def get_reverse_name(cls, field_name: str) -> str:
        field_type, field = cls.get_field_type_and_instance(field_name)
        assert field_type.is_relational(), f'{cls}, {field_name}, {field_type}'
        if field_type.is_pk_relation():
            return field.reference.related_name
        elif field_type.is_back_relation():
            return field.relation_field
        else:
            return field.related_name

    @classmethod
    def get_repo_name(cls) -> str:
        return cls._REPOSITORY_NAME

    @classmethod
    def entity(cls):
        repo_name = cls.get_repo_name()
        if repo_name != '__default__':
            return f'{cls.opts().full_name}.{repo_name}'
        return cls.opts().full_name

    @classmethod
    def get_field_name_for_value(cls, name: str) -> str:
        if name in cls.calculated:
            return name
        field_type = cls.get_field_type(name)
        if field_type.is_pk_relation():
            field = cls.get_field_instance(name)
            name = field.reference.model_field_name
        return name

    @classmethod
    def get_instance_value(cls, instance: MODEL, name: str) -> str:
        field_name = cls.get_field_name_for_value(name)
        return getattr(instance, field_name, UndefinedValue)


class ReadRepository(BaseRepository[MODEL]):

    def __init__(
            self,
            select_related: tuple[str, ...] = EMPTY_TUPLE,
            prefetch_related: tuple[str, ...] = EMPTY_TUPLE,
            annotations: dict[str, ...] = None,
    ):
        self.select_related = select_related
        self.prefetch_related = prefetch_related
        self.annotations = annotations

    def get_queryset(self):
        query = self.model.all()
        if default_filters := self.qs_default_filters():
            query = query.filter(*default_filters)
        if annotate_fields := {**self.qs_annotate_fields(), **(self.annotations or {})}:
            query = query.annotate(**annotate_fields)
        if final_select_related := {*self.qs_select_related(), *self.select_related}:
            query = query.select_related(*final_select_related)
        if final_prefetch_related := {*self.qs_prefetch_related(), *self.prefetch_related}:
            query = query.prefetch_related(*final_prefetch_related)
        return query

    def qs_default_filters(self) -> list[Q]:
        return []

    def qs_annotate_fields(self) -> dict[str, ...]:
        return {}

    def qs_select_related(self) -> tuple[str, ...]:
        return EMPTY_TUPLE

    def qs_prefetch_related(self) -> tuple[str, ...]:
        return EMPTY_TUPLE

    async def get_all(
            self,
            skip: Optional[int],
            limit: Optional[int],
            sort: list[str],
            filters: list[Filter],
    ) -> tuple[list[MODEL], int]:
        query = self.get_queryset()
        for f in filters:
            query = f.filter(query)
        count_query = query.count()
        if sort:
            query = query.order_by(*sort)
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        async with in_transaction():
            result = await query
            count = await count_query
        return result, count

    def _get_many_queryset(self, item_pk_list: list[PK]) -> QuerySet[MODEL]:
        return self.get_queryset().filter(pk__in=item_pk_list)

    async def get_many(self, item_pk_list: list[PK]) -> list[MODEL]:
        return await self._get_many_queryset(item_pk_list)

    @overload
    async def get_one(self, value: PK) -> MODEL: ...

    @overload
    async def get_one(self, value: ..., *, field_name: str) -> MODEL: ...

    async def get_one(self, value, *, field_name='pk') -> MODEL:
        if self.model.is_case_insensitive(field_name):
            field_name = field_name + '__iexact'
        instance = await self.get_queryset()\
            .get_or_none(**{field_name: value})
        if instance is None:
            raise ItemNotFound()
        return instance

