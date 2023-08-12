from typing import Optional

from tortoise import fields, validators


class FloatField(fields.FloatField):
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def __init__(
            self,
            min_value: float | int = None,
            max_value: float | int = None,
            editable: bool = True,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.editable = editable
        if min_value is not None:
            self.min_value = float(min_value)
            self.validators.append(validators.MinValueValidator(self.min_value))
        if max_value is not None:
            self.max_value = float(max_value)
            self.validators.append(validators.MaxValueValidator(self.max_value))

    @property
    def constraints(self) -> dict:
        return {
            'ge': self.min_value,
            'le': self.max_value,
            'editable': self.editable,
        }
