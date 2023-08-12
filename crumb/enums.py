from enum import StrEnum


__all__ = ["FieldTypes", "NotifyStatus"]


class FieldTypes(StrEnum):
    INT = 'int'
    FLOAT = 'float'
    STR = 'str'
    TEXT = 'text'
    BOOL = 'bool'
    ENUM = 'enum'
    DATE = 'date'
    DATETIME = 'datetime'
    O2O = 'o2o'
    O2O_PK = 'o2o_pk'
    FK = 'fk'
    FK_PK = 'fk_pk'
    BACK_O2O = 'back_o2o'
    BACK_FK = 'back_fk'
    HIDDEN = 'hidden'

    def is_hidden(self):
        return self is FieldTypes.HIDDEN

    @classmethod
    def db_field_types(cls):
        return (
            cls.INT,
            cls.FLOAT,
            cls.STR,
            cls.TEXT,
            cls.BOOL,
            cls.ENUM,
            cls.DATE,
            cls.DATETIME,
        )

    def is_db_field(self):
        return self in self.db_field_types()

    @classmethod
    def numeric_types(cls):
        return (
            cls.INT,
            cls.FLOAT
        )

    def is_numeric(self):
        return self in self.numeric_types()

    @classmethod
    def relational(cls):
        return (
            cls.O2O,
            cls.O2O_PK,
            cls.FK,
            cls.FK_PK,
            cls.BACK_O2O,
            cls.BACK_FK,
        )

    def is_relational(self):
        return self in self.relational()

    @classmethod
    def pk_relation(cls):
        return (
            cls.O2O_PK,
            cls.FK_PK
        )

    def is_pk_relation(self):
        return self in self.pk_relation()

    @classmethod
    def no_pk_relation(cls):
        return (
            cls.O2O,
            cls.FK,
            cls.BACK_O2O,
            cls.BACK_FK,
        )

    def is_no_pk_relation(self):
        return self in self.no_pk_relation()

    @classmethod
    def single_relation(cls):
        return (
            cls.O2O,
            cls.O2O_PK,
            cls.FK,
            cls.FK_PK,
            cls.BACK_O2O,
        )

    def is_single_relation(self):
        return self in self.single_relation()

    @classmethod
    def back_relation(cls):
        return (
            cls.BACK_FK,
            cls.BACK_O2O
        )

    def is_back_relation(self):
        return self in self.back_relation()

    @classmethod
    def multiple_relation(cls):
        return (
            cls.BACK_FK,
        )

    def is_multiple_relation(self):
        return self in self.multiple_relation()


class NotifyStatus(StrEnum):
    INFO = 'info'
    SUCCESS = 'success'
    WARN = 'warn'
    ERROR = 'error'
