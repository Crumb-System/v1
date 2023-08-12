from crumb.entities.registers import BaseRegister, BaseRegisterResult


__all__ = ["AccumRegister", "AccumRegisterResult"]


class AccumRegister(BaseRegister):
    count: int | float

    class Meta:
        abstract = True


class AccumRegisterResult(BaseRegisterResult):
    count: int | float

    class Meta:
        abstract = True
