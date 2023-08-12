from tortoise import fields, validators


class IntField(fields.IntField):

    def __init__(
            self,
            editable: bool = True,
            min_value: int = None,
            max_value: int = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.editable = False if self.generated else editable
        self.min_value = min_value
        self.max_value = max_value
        if self.min_value is not None:
            assert self.min_value >= -2147483648
            self.validators.append(validators.MinValueValidator(self.min_value))
        if self.max_value is not None:
            assert self.max_value <= 2147483648
            self.validators.append(validators.MaxValueValidator(self.max_value))

    @property
    def constraints(self) -> dict:
        result = super().constraints
        result['editable'] = self.reference.constraints.get('editable', True) if self.reference else self.editable
        if self.min_value is not None:
            result['ge'] = self.min_value
        if self.max_value is not None:
            result['le'] = self.max_value
        return result


class SmallIntField(fields.SmallIntField):

    def __init__(
            self,
            editable: bool = True,
            min_value: int = None,
            max_value: int = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.editable = False if self.generated else editable
        self.min_value = min_value
        self.max_value = max_value
        if self.min_value is not None:
            assert self.min_value >= -32768
            self.validators.append(validators.MinValueValidator(self.min_value))
        if self.max_value is not None:
            assert self.max_value <= 32768
            self.validators.append(validators.MaxValueValidator(self.max_value))

    @property
    def constraints(self) -> dict:
        result = super().constraints
        result['editable'] = self.reference.constraints.get('editable', True) if self.reference else self.editable
        if self.min_value is not None:
            result['ge'] = self.min_value
        if self.max_value is not None:
            result['le'] = self.max_value
        return result


class BigIntField(fields.BigIntField):
    def __init__(
            self,
            editable: bool = True,
            min_value: int = None,
            max_value: int = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.editable = False if self.generated else editable
        self.min_value = min_value
        self.max_value = max_value
        if self.min_value is not None:
            assert self.min_value >= -9223372036854775808
            self.validators.append(validators.MinValueValidator(self.min_value))
        if self.max_value is not None:
            assert self.max_value <= 9223372036854775807
            self.validators.append(validators.MaxValueValidator(self.max_value))

    @property
    def constraints(self) -> dict:
        result = super().constraints
        result['editable'] = self.reference.constraints.get('editable', True) if self.reference else self.editable
        if self.min_value is not None:
            result['ge'] = self.min_value
        if self.max_value is not None:
            result['le'] = self.max_value
        return result

