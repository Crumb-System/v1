from tortoise import fields
from tortoise.validators import MinLengthValidator, MaxLengthValidator
from tortoise.exceptions import ConfigurationError


class TextField(fields.TextField):
    def __init__(
            self,
            min_length: int = None,
            max_length: int = None,
            editable: bool = True,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.editable = editable
        if self.min_length is not None:
            if self.min_length < 1:
                raise ConfigurationError("'min_length' must be >= 1")
            self.validators.append(MinLengthValidator(self.min_length))
        if self.max_length is not None:
            if self.max_length < 1:
                raise ConfigurationError("'min_length' must be >= 1")
            self.validators.append(MaxLengthValidator(self.max_length))
        if self.min_length and self.max_length and self.min_length > self.max_length:
            raise ConfigurationError("'max_length' must be >= 'min_length'")

    @property
    def constraints(self) -> dict:
        return {
            'min_length': self.min_length,
            'max_length': self.max_length,
        }
