from .base import EqualFilter, InFilter, LessFilter, MoreFilter

__all__ = ["IntEqualFilter", "IntInFilter", "IntLessFilter", "IntMoreFilter"]


class IntEqualFilter(EqualFilter[int]):
    pass


class IntInFilter(InFilter[int]):
    pass


class IntLessFilter(LessFilter[int]):
    pass


class IntMoreFilter(MoreFilter[int]):
    pass
