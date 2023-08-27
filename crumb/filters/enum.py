from enum import Enum

from .base import EqualFilter

__all__ = ["EnumEqualFilter"]


class EnumEqualFilter(EqualFilter[Enum]):
    pass
