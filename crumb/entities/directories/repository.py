from typing import TypeVar

from crumb.repository import Repository, ValuesListRepository
from crumb.entities.directories import Directory, DirectoryListValue


__all__ = ["DirectoryRepository"]


DirectoryModel = TypeVar('DirectoryModel', bound=Directory)
DirectoryListValueModel = TypeVar('DirectoryListValueModel', bound=DirectoryListValue)


class DirectoryRepository(Repository[DirectoryModel]):
    pass
