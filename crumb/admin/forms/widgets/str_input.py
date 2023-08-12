from dataclasses import dataclass
from typing import Optional, TypeVar

from crumb.admin.exceptions import InputValidationError
from .input import InputWidget, Input


class StrInputWidget(InputWidget[str]):

    @property
    def final_value(self) -> Optional[str]:
        if self.value == '' and self.null and self.empty_as_none:
            return None
        return self.value

    def __init__(
            self,
            *,
            max_length: Optional[int] = None,
            min_length: Optional[int] = None,
            empty_as_none: bool = False,
            is_password: bool = False,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.min_length = min_length
        self.empty_as_none = empty_as_none
        if is_password:
            self.password = True
        self.__finalize_init__()

    @property
    def password(self):
        return self.input.password

    @password.setter
    def password(self, v: bool):
        self.input.password = v

    @property
    def value(self):
        return self.input.value

    @value.setter
    def value(self, v: str):
        self.text.value = '•' * len(v) if self.password else v
        self.input.value = v

    def _validate(self) -> None:
        if self.value == '':
            if self.required:
                raise InputValidationError(msg='Поле обязательно')
            return
        if self.max_length is not None and len(self.value) > self.max_length:
            raise InputValidationError(msg=f'Максимум символов - {self.max_length}')
        if self.min_length is not None and len(self.value) < self.min_length:
            raise InputValidationError(msg=f'Минимум символов - {self.min_length}')

    def set_value(self, value: str, initial: bool = False):
        assert value is None or isinstance(value, str)
        self.value = value or ''


S = TypeVar('S', bound=StrInputWidget)


@dataclass
class StrInput(Input[S]):
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    empty_as_none: bool = False
    is_password: bool = False
    default: str = ''

    @property
    def widget_type(self):
        return StrInputWidget
