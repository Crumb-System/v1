import json

from flet import Text

from crumb.exceptions import ObjectErrors
from crumb.admin.components.errors.base import ErrorContainer


class ObjectErrorsContainer(ErrorContainer[ObjectErrors]):
    default_title = 'Ошибка валидации'

    def get_error_text(self) -> Text:
        return Text(json.dumps(self.error.to_error(), ensure_ascii=False, indent=4))
