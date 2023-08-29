from datetime import datetime

from tortoise import timezone

from crumb.filters.base import LessFilter, MoreFilter


__all__ = ["DatetimeLessFilter", "DatetimeMoreFilter", "DatetimePastFilter", "DatetimeFutureFilter"]


class DatetimeLessFilter(LessFilter[datetime]):
    pass


class DatetimeMoreFilter(MoreFilter[datetime]):
    pass


class DatetimePastFilter(DatetimeLessFilter):
    @classmethod
    def value_factory(cls):
        return timezone.now()


class DatetimeFutureFilter(DatetimeMoreFilter):
    @classmethod
    def value_factory(cls):
        return timezone.now()
