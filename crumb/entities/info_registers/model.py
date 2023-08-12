from crumb.entities.registers import BaseRegister, BaseRegisterResult


__all__ = ["InfoRegister", "InfoRegisterResult"]


class InfoRegister(BaseRegister):
    class Meta:
        abstract = True


class InfoRegisterResult(BaseRegisterResult):
    class Meta:
        abstract = True
