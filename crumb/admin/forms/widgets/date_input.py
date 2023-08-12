from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from flet import KeyboardType

from crumb.admin.exceptions import InputValidationError
from .input import InputWidget, Input


class DateInputWidget(InputWidget[date]):
    date_fmt = '%d.%m.%Y'
    real_value: Optional[date]

    @property
    def final_value(self) -> Optional[date]:
        return self.real_value

    def __init__(
            self,
            *,
            min_date: Optional[date] = None,
            max_date: Optional[date] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.keyboard_type = KeyboardType.DATETIME
        self.min_date = min_date
        self.max_date = max_date
        self.__finalize_init__()

    def to_date(self, value: str) -> Optional[date]:
        if value == '':
            return
        return datetime.strptime(value, self.date_fmt).date()

    def _validate(self) -> None:
        if self.real_value is None:
            if self.value != '':
                raise InputValidationError('Неверный формат')
            if self.required:
                raise InputValidationError('Обязательное поле')
            return None
        if self.min_date is not None and self.real_value < self.min_date:
            raise InputValidationError(f'Минимум {self.min_date.strftime(self.date_fmt)}')
        if self.max_date is not None and self.real_value > self.max_date:
            raise InputValidationError(f'Максимум {self.max_date.strftime(self.date_fmt)}')

    def set_value(self, value: Optional[str | date], initial: bool = False):
        assert value is None or isinstance(value, (str, date))
        if value is None:
            self.real_value = None
            self.value = ''
        elif isinstance(value, str):
            self.value = value
            try:
                self.real_value = self.to_date(value)
            except ValueError:
                self.real_value = None
        else:
            self.real_value = value
            self.value = value.strftime(self.date_fmt)


@dataclass
class DateInput(Input[DateInputWidget]):
    min_date: Optional[date] = None
    max_date: Optional[date] = None

    @property
    def widget_type(self):
        return DateInputWidget
