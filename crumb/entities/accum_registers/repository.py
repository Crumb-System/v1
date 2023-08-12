from datetime import datetime
from typing import TypeVar, Any

from tortoise.functions import Sum

from crumb.entities.registers import BaseRegisterRepository
from .model import AccumRegister, AccumRegisterResult


__all__ = ["AccumRegisterRepository"]


AR = TypeVar('AR', bound=AccumRegister)
ARR = TypeVar('ARR', bound=AccumRegisterResult)


class AccumRegisterRepository(BaseRegisterRepository[AR, ARR]):
    main_field: str = 'count'

    @classmethod
    async def calc_results(cls, time_point: datetime = None) -> list[dict[str, Any]]:
        query = cls.model.annotate(result=Sum(cls.main_field))
        if time_point:
            query = query.filter(dt__le=time_point)
        return await query.group_by(*cls.group_by).values(*cls.group_by, 'result')
