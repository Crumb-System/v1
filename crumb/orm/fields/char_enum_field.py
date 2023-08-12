from enum import Enum
from typing import Type, Optional

from tortoise import fields


class CharEnumFieldInstance(fields.data.CharEnumFieldInstance):
    def __init__(
            self,
            enum_type: Type[Enum],
            description: Optional[str] = None,
            max_length: int = 0,
            editable: bool = True,
            **kwargs,
    ):
        super().__init__(enum_type, description, max_length, **kwargs)
        self.editable = editable

    @property
    def constraints(self) -> dict:
        result = super().constraints
        result['editable'] = self.editable
        return result


def CharEnumField(
        enum_type: Type[fields.data.CharEnumType],
        description: Optional[str] = None,
        max_length: int = 0,
        editable: bool = True,
        **kwargs,
) -> fields.data.CharEnumType:
    return CharEnumFieldInstance(  # type: ignore
        enum_type,
        description,
        max_length,
        editable,
        ** kwargs
    )
