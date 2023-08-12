from enum import IntEnum
from typing import Type, Optional

from tortoise import fields


class IntEnumFieldInstance(fields.data.IntEnumFieldInstance):
    def __init__(
            self,
            enum_type: Type[IntEnum],
            description: Optional[str] = None,
            generated: bool = False,
            editable: bool = True,
            **kwargs,
    ):
        super().__init__(enum_type, description, generated, **kwargs)
        self.editable = False if self.generated else editable

    @property
    def constraints(self) -> dict:
        result = super().constraints
        result['editable'] = self.editable
        return result


def IntEnumField(
        enum_type: Type[fields.data.IntEnumType],
        description: Optional[str] = None,
        editable: bool = True,
        **kwargs
) -> fields.data.IntEnumType:
    return IntEnumFieldInstance(  # type: ignore
        enum_type,
        description,
        editable,
        **kwargs,
    )
