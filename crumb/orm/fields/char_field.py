from tortoise import fields
from tortoise.validators import MinLengthValidator
from tortoise.exceptions import ConfigurationError


class CharField(fields.CharField):

    def __init__(
            self,
            min_length: int = None,
            editable: bool = True,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.editable = editable
        if self.min_length is not None:
            if self.min_length < 1:
                raise ConfigurationError("'min_length' must be >= 1")
            self.validators.append(MinLengthValidator(self.min_length))
        if self.min_length and self.max_length and self.min_length > self.max_length:
            raise ConfigurationError("'max_length' must be >= 'min_length'")

    @property
    def constraints(self) -> dict:
        return {
            "min_length": self.min_length,
            "max_length": self.max_length,
            "editable": self.reference.constraints.get('editable', True) if self.reference else self.editable
        }
