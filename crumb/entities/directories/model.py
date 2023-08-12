from crumb.orm.base_model import BaseModel, ListValueModel


__all__ = ["Directory", "DirectoryListValue"]


class Directory(BaseModel):
    class Meta:
        abstract = True


class DirectoryListValue(ListValueModel):
    class Meta:
        abstract = True
