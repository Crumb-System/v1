from enum import Enum
from typing import Iterable

from .base import EqualFilter, InFilter

__all__ = ["EnumEqualFilter", "EnumInFilter"]


class EnumEqualFilter(EqualFilter[Enum]):
    pass


class EnumInFilter(InFilter[Iterable[Enum]]):
    pass
