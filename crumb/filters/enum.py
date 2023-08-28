from enum import Enum

from .base import EqualFilter, InFilter

__all__ = ["EnumEqualFilter", "EnumInFilter"]


class EnumEqualFilter(EqualFilter[Enum]):
    pass


class EnumInFilter(InFilter[Enum]):
    pass
