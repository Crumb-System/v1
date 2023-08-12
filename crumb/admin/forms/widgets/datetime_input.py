from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from flet import KeyboardType
from tortoise import timezone

from crumb.admin.exceptions import InputValidationError
from .input import InputWidget, Input


class DatetimeInputWidget(InputWidget[datetime]):
    dt_fmt = '%d.%m.%Y %H:%M:%S'
    real_value: Optional[datetime]

    @property
    def final_value(self) -> Optional[datetime]:
        return self.real_value

    def __init__(
            self,
            *,
            min_dt: Optional[datetime] = None,
            max_dt: Optional[datetime] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.keyboard_type = KeyboardType.DATETIME
        self.min_dt = min_dt
        self.max_dt = max_dt
        self.__finalize_init__()

    @classmethod
    def to_datetime(cls, value: str) -> Optional[datetime]:
        if value == '':
            return
        return timezone.make_aware(datetime.strptime(value, cls.dt_fmt))

    def _validate(self) -> None:
        if self.real_value is None:
            if self.value != '':
                raise InputValidationError('Неверный формат')
            if self.required:
                raise InputValidationError('Обязательное поле')
            return None
        if self.min_dt is not None and self.real_value < self.min_dt:
            raise InputValidationError(f'Минимум {self.min_dt.strftime(self.dt_fmt)}')
        if self.max_dt is not None and self.real_value > self.max_dt:
            raise InputValidationError(f'Максимум {self.max_dt.strftime(self.dt_fmt)}')

    def set_value(self, value: Optional[str | datetime], initial: bool = False) -> None:
        assert value is None or isinstance(value, (str, datetime))
        if value is None:
            self.value = ''
            self.real_value = None
        elif isinstance(value, str):
            self.value = value
            try:
                self.real_value = self.to_datetime(value)
            except ValueError:
                self.real_value = None
        else:
            if timezone.is_aware(value):
                self.real_value = value
                self.value = timezone.make_naive(value).strftime(self.dt_fmt)
            else:
                self.real_value = timezone.make_aware(value)
                self.value = value.strftime(self.dt_fmt)


@dataclass
class DatetimeInput(Input[DatetimeInputWidget]):
    min_dt: Optional[datetime] = None
    max_dt: Optional[datetime] = None

    @property
    def widget_type(self):
        return DatetimeInputWidget
