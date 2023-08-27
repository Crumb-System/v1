from dataclasses import dataclass
from typing import Optional

from flet import KeyboardType

from crumb.admin.exceptions import InputValidationError
from .input import InputWidget, Input


class FloatInputWidget(InputWidget[float]):

    @property
    def final_value(self) -> float:
        return None if self.value == '' else round(float(self.value), self.decimal_places)

    def __init__(
            self,
            *,
            min_value: Optional[float | int] = None,
            max_value: Optional[float | int] = None,
            decimal_places: int = 2,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.keyboard_type = KeyboardType.NUMBER

        self.min_value = min_value
        self.max_value = max_value
        self.decimal_places = decimal_places
        self.__finalize_init__()

    def _validate(self) -> None:
        empty = self.value == ''
        if self.required and empty:
            raise InputValidationError('Обязательное поле')
        if empty:
            return None
        try:
            num = float(self.value)
        except ValueError:
            raise InputValidationError('Введите число (с точкой)')
        if self.min_value is not None and num < self.min_value:
            raise InputValidationError(f'Минимум {self.min_value}')
        if self.max_value is not None and num > self.max_value:
            raise InputValidationError(f'Максимум {self.max_value}')

    def set_value(self, value: float | str, initial: bool = False):
        if isinstance(value, str):
            value = value.replace(',', '.') if ',' in value else value
            try:
                value = float(value)
            except ValueError:
                self.value = value
                return
        assert value is None or isinstance(value, float), f'value is {value}'
        if value is None:
            self.value = ''
        else:
            self.value = f'{float(value):.{self.decimal_places}f}'


@dataclass
class FloatInput(Input[FloatInputWidget]):
    min_value: Optional[float | int] = None
    max_value: Optional[float | int] = None
    decimal_places: int = 3
    default: float = 0.0

    @property
    def widget_type(self):
        return FloatInputWidget

    @property
    def is_numeric(self):
        return True
