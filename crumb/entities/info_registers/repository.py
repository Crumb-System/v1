from datetime import datetime
from typing import TypeVar, Any

from tortoise.transactions import in_transaction

from crumb.entities.registers import BaseRegisterRepository
from .model import InfoRegister, InfoRegisterResult


__all__ = ["InfoRegisterRepository"]


IR = TypeVar('IR', bound=InfoRegister)
IRR = TypeVar('IRR', bound=InfoRegisterResult)


class InfoRegisterRepository(BaseRegisterRepository[IR, IRR]):

    @classmethod
    async def calc_results(cls, time_point: datetime = None) -> list[dict[str, Any]]:
        partition_by = ', '.join(f'"{f}"' for f in cls.group_by)
        async with in_transaction() as conn:
            _, rows = await conn.execute_query(
                f'SELECT * '
                f'FROM ('
                f'    SELECT '
                f'        {partition_by}, '
                f'        "{cls.main_field}" as "result", '
                f'        ROW_NUMBER() OVER (PARTITION BY {partition_by} ORDER BY "dt" DESC) as "rn" '
                f'    FROM {cls.opts().db_table} '
                f') sub '
                f'WHERE rn=1 {"AND dt <= ?" if time_point else ""}',
                values=[time_point] if time_point else None
            )
        return rows

    @classmethod
    async def get_results(cls, item_pks: list):
        raise NotImplementedError()
