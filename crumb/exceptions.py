from typing import Union, Type, Self, Sequence, Optional


class ItemNotFound(ValueError):
    """Выбрасывается Repository.get_one() если объект не найден"""


class UnexpectedDataKey(ValueError):
    """Выбрасывается, если в фукнцию создния или изменения элемента прилетает поле, которого там не может быть"""


class InvalidType(ValueError):
    """Выбрасывается, когда в репозиторий передано значение не того типа"""


class NotAuthenticated(ValueError):
    """Выбрасывается, когда пользователь ввел неправильный логин или пароль"""


class FieldError(Exception):
    key: str
    msg: str

    def to_error(self):
        return {'key': self.key, 'msg': self.msg}


class AnyFieldError(FieldError):
    def __init__(self, key: str, msg: str = None):
        self.key = key
        self.msg = msg

    def to_error(self):
        return {'key': self.key, 'msg': self.msg}


NotUnique = AnyFieldError('not_unique', 'Значение не уникально')
NotFoundFK = AnyFieldError('not_found_fk', 'Запись в БД не найдена')
NotFound = AnyFieldError('not_found', 'Запись в БД не найдена')
FieldRequired = AnyFieldError('required_field', 'Обязательное поле')
OldPasswordIsIncorrect = AnyFieldError('old_password_is_incorrect', 'Старый пароль неверный')


class NotUniqueTogether(FieldError):
    key: str = 'not_unique_together'
    msg: str = 'Комбинация не уникальна {}'
    fields: Sequence[str]

    def __init__(self, fields: Sequence[str]):
        self.fields = fields

    def to_error(self):
        return {
            'key': self.key,
            'msg': self.msg.format(', '.join(self.fields)),
            'fields': self.fields,
        }


class RequiredMissed(FieldError):
    key: str = 'required_missed'
    msg: str = 'Пропущено обязательное поле'
    field_name: str
    related: Optional[str]

    def __init__(self, field_name: str, related: Optional[str]):
        self.field_name = field_name
        self.related = related

    def to_error(self):
        return {
            'key': self.key,
            'msg': f'{self.msg} {self.field_name}{" или " + self.related if self.related else ""}',
            'field_name': self.field_name,
            'related': self.related,
        }


class ListFieldError(FieldError):

    def __init__(self,  *args):
        super().__init__(*args)
        self.objects_map: dict[int, Union["ObjectErrors", "FieldError"]] = {}

    def append(self, index: int, err: Union[Type["FieldError"], "FieldError", "ObjectErrors"]):
        self.objects_map[index] = err

    def to_error(self):
        return {index: error.to_error() for index, error in self.objects_map.items()}

    def __bool__(self):
        return len(self.objects_map) > 0

    def __contains__(self, item: int):
        return item in self.objects_map

    def __getitem__(self, item: int):
        return self.objects_map[item]


class ObjectErrors(Exception):
    errors: dict[str, Union[Type["FieldError"], "FieldError", "ObjectErrors"]]
    _root: list[FieldError]

    def __init__(self, *args):
        super().__init__(*args)
        self.errors = {}
        self._root = []

    def __str__(self):
        return str(self.to_error())

    def to_error(self):
        errors = {key: error.to_error() for key, error in self.errors.items()}
        if self.root:
            errors['__root__'] = [err.to_error() for err in self.root]
        return errors

    def add(self, field: str, error: Union[Type["FieldError"], "FieldError", "ObjectErrors"]) -> Self:
        if field == '__root__':
            self.root = error
        else:
            self.errors[field] = error
        return self

    def merge(self, obj_error: "ObjectErrors") -> Self:
        self.errors.update(obj_error.errors)
        self._root.extend(obj_error.root)
        return self

    def __bool__(self) -> bool:
        return not not (self.errors or self._root)

    @property
    def root(self) -> list[FieldError]:
        return self._root

    @root.setter
    def root(self, value: FieldError) -> None:
        self._root.append(value)
