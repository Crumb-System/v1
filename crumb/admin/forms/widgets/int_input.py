from dataclasses import dataclass
from typing import Optional

from flet import KeyboardType

from crumb.admin.exceptions import InputValidationError
from .input import InputWidget, Input


class IntInputWidget(InputWidget[int]):
    @property
    def final_value(self) -> int:
        return None if self.value == '' else int(self.value)

    def __init__(
            self,
            *,
            min_value: Optional[int] = None,
            max_value: Optional[int] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.keyboard_type = KeyboardType.NUMBER

        self.min_value = min_value
        self.max_value = max_value
        self.__finalize_init__()

    def _validate(self) -> None:
        empty = self.value == ''
        if self.required and empty:
            raise InputValidationError('Обязательное поле')
        if empty:
            return None
        try:
            num = int(self.value)
        except ValueError:
            raise InputValidationError('Введите число')
        if self.min_value is not None and num < self.min_value:
            raise InputValidationError(f'Минимум {self.min_value}')
        if self.max_value is not None and num > self.max_value:
            raise InputValidationError(f'Максимум {self.max_value}')

    def set_value(self, value: int, initial: bool = False):
        if isinstance(value, str):
            value = ''.join(v for v in value if v.isdigit())
            try:
                value = int(value)
            except ValueError:
                self.value = value
                return
        assert value is None or isinstance(value, int)
        self.value = '' if value is None else str(value)


@dataclass
class IntInput(Input[IntInputWidget]):
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    default: int = 0

    @property
    def widget_type(self):
        return IntInputWidget

    @property
    def is_numeric(self):
        return True
