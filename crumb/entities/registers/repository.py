from datetime import datetime
from typing import Generic, TypeVar, TYPE_CHECKING, Any

from crumb.repository.base import ReadRepository
from .model import BaseRegister, BaseRegisterResult
from ...constants import EMPTY_TUPLE

if TYPE_CHECKING:
    from crumb.entities.documents import Document


R = TypeVar('R', bound=BaseRegister)
RR = TypeVar('RR', bound=BaseRegisterResult)


__all__ = ["BaseRegisterRepository"]


class BaseRegisterRepository(Generic[R, RR], ReadRepository[R]):
    results: ReadRepository[RR]
    group_by: tuple[str, ...]
    main_field: str
    side_fields: tuple[str] = EMPTY_TUPLE

    @classmethod
    async def register(
            cls,
            registrator: "Document",
            records: list[dict[str, Any]],
    ):
        reg_number = registrator.unique_number
        reg_dt = registrator.dt
        instances: list[R] = [
            cls.model(
                registrator=reg_number,
                dt=reg_dt,
                **{name: rec[name] for name in (*cls.group_by, cls.main_field, *cls.side_fields)},
            )
            for rec in records
        ]
        instances = await cls.model.bulk_create(instances, batch_size=100)
        await cls.update_results(instances)

    @classmethod
    async def unregister(cls, registrator: "Document"):
        reg_number = registrator.unique_number
        instances = await cls.model.filter(registrator=reg_number)
        await cls.model.filter(registrator=reg_number).delete()
        await cls.update_results(instances)

    @classmethod
    async def calc_results(
            cls,
            time_point: datetime = None
    ) -> list[dict[str, Any]]:
        pass

    @classmethod
    async def set_results(cls, values: list[dict[str, Any]]):
        instances = []
        for value in values:
            instance: RR = cls.results.model()
            for field in cls.group_by:
                setattr(instance, field, value[field])
            setattr(instance, cls.main_field, value['result'])
            instance.id = ','.join(str(getattr(instance, field_name)) for field_name in cls.group_by)
            instances.append(instance)
        await cls.results.model.bulk_create(instances)

    @classmethod
    async def reset_results(cls):
        await cls.results.model.all().delete()
        await cls.set_results(await cls.calc_results())

    @classmethod
    async def update_results(cls, instances: list[R]):
        # groups = [
        #     tuple(getattr(instance, field_name) for field_name in cls.group_by)
        #     for instance in instances
        # ]
        # await cls.set_results(await cls.calc_results(groups=groups))
        # TODO: сделать, чтобы обновлять можно было частично
        await cls.reset_results()
