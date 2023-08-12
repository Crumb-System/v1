from typing import TypeVar

from crumb.entities.directories import DirectoryRepository

from crumb.admin.forms import DirectoryInputForm
from crumb.admin.resources.crud_resource import CrudResource


REP = TypeVar("REP", bound=DirectoryRepository)


class DirectoryResource(CrudResource[REP]):
    model_form = DirectoryInputForm
