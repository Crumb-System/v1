from typing import TYPE_CHECKING, Any, Union, overload, Callable, Type

from tortoise import fields

from crumb.admin.forms.widgets import ObjectTableRow, IntInput
from crumb.orm import fields as orm_fields
from crumb.enums import FieldTypes
from crumb.types import FK_TYPE
from crumb.admin.forms import Primitive, PRIMITIVE_ITEM, InputGroup, widgets

if TYPE_CHECKING:
    from crumb.admin.resources import Resource


class WidgetSchemaCreator:
    """Автосоставление схем виджетов для зарегистрированных в модели полей"""

    def __init__(
            self,
            resource: "Resource",
            all_read_only: bool = False,
            allow_groups: bool = True,
    ):
        self.resource = resource
        self.repository = self.resource.repository
        self.all_read_only = all_read_only
        self.allow_groups = allow_groups

    @classmethod
    def _widget_schema_classes(cls):
        return {
            FieldTypes.INT: widgets.IntInput,
            FieldTypes.FLOAT: widgets.FloatInput,
            FieldTypes.STR: widgets.StrInput,
            FieldTypes.TEXT: widgets.TextInput,
            FieldTypes.BOOL: widgets.Checkbox,
            FieldTypes.ENUM: widgets.EnumChoice,
            FieldTypes.DATE: widgets.DateInput,
            FieldTypes.DATETIME: widgets.DatetimeInput,
            FieldTypes.O2O: widgets.Object,
            FieldTypes.O2O_PK: widgets.RelatedChoice,
            FieldTypes.FK: widgets.Object,
            FieldTypes.FK_PK: widgets.RelatedChoice,
            FieldTypes.BACK_O2O: widgets.Object,
            FieldTypes.BACK_FK: widgets.TableInput,
        }

    def _creators(self):
        return {
            FieldTypes.INT: self.int,
            FieldTypes.FLOAT: self.float,
            FieldTypes.STR: self.str,
            FieldTypes.TEXT: self.text,
            FieldTypes.BOOL: self.checkbox,
            FieldTypes.ENUM: self.enum,
            FieldTypes.DATE: self.date,
            FieldTypes.DATETIME: self.datetime,
            FieldTypes.O2O: self.object,
            FieldTypes.O2O_PK: self.related_choice,
            FieldTypes.FK: self.object,
            FieldTypes.FK_PK: self.related_choice,
            FieldTypes.BACK_O2O: self.object,
            FieldTypes.BACK_FK: self.table_input,
        }

    @property
    def creators(self) -> dict[FieldTypes, Callable[[fields.Field, ...], widgets.UserInput]]:
        if not hasattr(self, '_cached_creators'):
            setattr(self, '_cached_creators', self._creators())
        return getattr(self, '_cached_creators')

    @property
    def widget_schema_classes(self) -> dict[FieldTypes, Type[widgets.UserInput]]:
        if not hasattr(self, '_cached_widget_schema_classes'):
            setattr(self, '_cached_widget_schema_classes', self._widget_schema_classes())
        return getattr(self, '_cached_widget_schema_classes')

    def from_primitive_item(self, item: PRIMITIVE_ITEM) -> widgets.UserInput | InputGroup:
        if Primitive.is_schema(item):
            return item
        elif Primitive.is_group(item):
            assert self.allow_groups
            group_field = item.get('primitive')
            group = InputGroup(**{k: v for k, v in item.items() if k != 'primitive'})
            for f in group_field:
                group.add_field(self.from_primitive_item(f))
            return group
        elif Primitive.is_field_with_extra(item):
            field_name, extra = item
        else:
            raise ValueError(f'{type(item)}({item}) не подходит ни под какой из типов:)')
        if field_name in self.repository.calculated:
            label = self.resource.translate_field(field_name)
            field_type = self.repository.calculated[field_name]
            if isinstance(field_type, tuple):
                field_type, common_extra = field_type
                extra = {**common_extra, **extra}
            return self.widget_schema_classes[field_type](**{  # type: ignore
                'name': field_name,
                'label': label,
                'editable': False,
                'ignore': True,
                **extra,
            })
        if field_name in self.repository.extra_allowed:
            label = self.resource.translate_field(field_name)
            field_type = self.repository.extra_allowed[field_name]
            if isinstance(field_type, tuple):
                field_type, common_extra = field_type
                extra = {**common_extra, **extra}
            return self.widget_schema_classes[field_type](**{  # type: ignore
                'name': field_name,
                'label': label,
                **extra
            })
        field_type, field = self.repository.get_field_type_and_instance(field_name)
        if field_type.is_hidden():
            raise ValueError(f'{field_name} in {self.repository} is hidden')
        creator = self.creators[field_type]
        return creator(field, **extra)

    @classmethod
    def pop_allowed_extra(cls, extra: dict[str, Any], *keys: str):
        return {k: extra.pop(k) for k in keys if k in extra} if extra else {}

    @classmethod
    def raise_if_unexpected_extra(cls, field: fields.Field, extra: dict[str, Any]):
        if extra:
            raise ValueError(
                f'{field.model.__name__}.{field.model_field_name} has unexpected extras: {",".join(k for k in extra)}'
            )

    def base_kwargs(self, field: fields.Field, extra: dict[str, Any]) -> dict[str, Any]:
        constraints = field.constraints
        kwargs = {
            'name': field.model_field_name,
            'label': self.resource.translate_field(field.model_field_name),
            'null': field.null,
            'required': self.repository.field_is_required(field),
            'editable': field.constraints.get('editable', True),
            'ignore_if_none': constraints.get('ignore_if_none', False),
            **self.pop_allowed_extra(
                extra,
                'name',
                'label',
                'null',
                'required',
                'editable',
                'ignore',
                'ignore_if_none',
                'default',
                'on_value_change',
                'helper_text',
                'width',
                'height',
                'resize_width',
                'resize_height',
                'min_width',
                'max_width',
                'min_height',
                'max_height',
            )
        }
        if self.all_read_only:
            kwargs['editable'] = False
        return kwargs

    def input_kwargs(self, field: fields.Field, extra: dict[str, Any]) -> dict[str, Any]:
        return self.base_kwargs(field, extra)

    def int(
            self,
            field: orm_fields.IntField | orm_fields.SmallIntField | orm_fields.BigIntField,
            **extra
    ) -> widgets.IntInput:
        kwargs = self.input_kwargs(field, extra)
        constraints = field.constraints
        kwargs['min_value'] = constraints['ge']
        kwargs['max_value'] = constraints['le']
        kwargs.update(self.pop_allowed_extra(extra, 'min_value', 'max_value'))
        self.raise_if_unexpected_extra(field, extra)
        return widgets.IntInput(**kwargs)

    def float(self, field: orm_fields.FloatField, **extra) -> widgets.FloatInput:
        kwargs = self.input_kwargs(field, extra)
        constraints = field.constraints
        kwargs['min_value'] = constraints['ge']
        kwargs['max_value'] = constraints['le']
        kwargs.update(self.pop_allowed_extra(extra, 'min_value', 'max_value', 'decimal_places'))
        self.raise_if_unexpected_extra(field, extra)
        return widgets.FloatInput(**kwargs)

    def str_or_text_kwargs(self, field: Union["orm_fields.CharField", "orm_fields.TextField"], extra) -> dict[str, Any]:
        kwargs = self.input_kwargs(field, extra)
        constraints = field.constraints
        kwargs['min_length'] = constraints['min_length']
        kwargs['max_length'] = constraints['max_length']
        kwargs['empty_as_none'] = kwargs['null']
        kwargs.update(self.pop_allowed_extra(
            extra,
            'max_length',
            'min_length',
            'empty_as_none',
        ))
        return kwargs

    def str(self, field: "orm_fields.CharField", **extra) -> widgets.StrInput:
        kwargs = self.str_or_text_kwargs(field, extra)
        kwargs.update(self.pop_allowed_extra(extra, 'is_password'))
        self.raise_if_unexpected_extra(field, extra)
        return widgets.StrInput(**kwargs)

    def text(self, field: "orm_fields.TextField", **extra) -> widgets.TextInput:
        kwargs = self.str_or_text_kwargs(field, extra)
        kwargs.update(self.pop_allowed_extra(extra, 'min_lines', 'max_lines'))
        self.raise_if_unexpected_extra(field, extra)
        return widgets.TextInput(**kwargs)

    def checkbox(self, field: "fields.BooleanField", **extra) -> widgets.Checkbox:
        kwargs = self.base_kwargs(field, extra)
        self.raise_if_unexpected_extra(field, extra)
        return widgets.Checkbox(**kwargs)

    def enum(
            self,
            field: Union["orm_fields.CharEnumFieldInstance", "orm_fields.IntEnumFieldInstance"],
            **extra
    ) -> widgets.EnumChoice:
        kwargs = self.base_kwargs(field, extra)
        kwargs['enum_type'] = field.enum_type
        kwargs.update(self.pop_allowed_extra(extra, 'enum_type'))
        self.raise_if_unexpected_extra(field, extra)
        return widgets.EnumChoice(**kwargs)

    def date(self, field: "fields.DateField", **extra) -> widgets.DateInput:
        kwargs = self.input_kwargs(field, extra)
        kwargs.update(self.pop_allowed_extra(extra, 'min_date', 'max_date'))
        self.raise_if_unexpected_extra(field, extra)
        return widgets.DateInput(**kwargs)

    def datetime(self, field: orm_fields.DatetimeField, **extra) -> widgets.DatetimeInput:
        kwargs = self.input_kwargs(field, extra)
        kwargs.update(self.pop_allowed_extra(extra, 'min_dt', 'max_dt'))
        self.raise_if_unexpected_extra(field, extra)
        return widgets.DatetimeInput(**kwargs)

    @overload
    def object(
            self,
            field: Union[
                "fields.relational.ForeignKeyFieldInstance",
                "fields.relational.OneToOneFieldInstance",
                "fields.relational.BackwardOneToOneRelation",
            ],
            **extra,
    ) -> widgets.Object: ...

    @overload
    def object(
            self,
            field: "fields.relational.BackwardFKRelation",
            **extra
    ) -> widgets.ObjectTableRow: ...

    def object(
            self,
            field: Union[
                "fields.relational.ForeignKeyFieldInstance",
                "fields.relational.OneToOneFieldInstance",
                "fields.relational.BackwardFKRelation",
                "fields.relational.BackwardOneToOneRelation",
            ],
            **extra,
    ) -> widgets.Object | widgets.ObjectTableRow:
        allowed_keys = ['fields']
        if field.__class__ is fields.relational.BackwardFKRelation:
            widget_class = widgets.ObjectTableRow
        else:
            widget_class = widgets.Object
            allowed_keys.append('variant')
        kwargs = self.base_kwargs(field, extra)
        kwargs['resource'] = relative_resource = self.resource.relative_resource(kwargs['name'])

        assert 'primitive' in extra or 'fields' in extra, f'{kwargs["name"]} must have primitive or fields'
        if 'fields' not in extra:
            primitive = extra.pop('primitive')
            assert isinstance(primitive, Primitive)
            relative_creator = WidgetSchemaCreator(
                resource=relative_resource,
                all_read_only=self.all_read_only
            )
            extra['fields'] = [
                relative_creator.from_primitive_item(item)
                for item in primitive
            ]

        kwargs.update(self.pop_allowed_extra(extra, *allowed_keys))
        self.raise_if_unexpected_extra(field, extra)
        return widget_class(**kwargs)

    def related_choice(
            self,
            field: FK_TYPE,
            **extra
    ) -> widgets.RelatedChoice:
        kwargs = self.base_kwargs(field, extra)
        if 'entity' not in extra:
            kwargs['entity'] = self.resource.relative_resource(field.model_field_name).entity()
        kwargs.update(self.pop_allowed_extra(extra, 'entity', 'method', 'query'))
        self.raise_if_unexpected_extra(field, extra)
        return widgets.RelatedChoice(**kwargs)

    def table_input(
            self,
            field: "fields.relational.BackwardFKRelation",
            **extra
    ) -> widgets.TableInput:
        kwargs = self.base_kwargs(field, extra)
        object_schema_info = extra.get('object_schema', {})
        if not isinstance(object_schema_info, widgets.ObjectTableRow):
            extra['object_schema'] = self.object(field, **object_schema_info)
        kwargs.update(self.pop_allowed_extra(
            extra,
            'object_schema',
            'variant',
            'rows_count',
        ))
        object_schema: ObjectTableRow = kwargs['object_schema']
        if not any(f.name == 'ordering' for f in object_schema.fields):
            object_schema.fields.insert(0, IntInput(name='ordering', label='№', editable=False, width=40))
        self.raise_if_unexpected_extra(field, extra)
        return widgets.TableInput(**kwargs)
