from .base import EqualFilter, InFilter

__all__ = ["IntEqualFilter", "IntInFilter"]


class IntEqualFilter(EqualFilter[int]):
    pass


class IntInFilter(InFilter[int]):
    pass
