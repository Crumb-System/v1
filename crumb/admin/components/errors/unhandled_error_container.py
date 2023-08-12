import traceback

from flet import Text

from crumb.admin.components.errors.base import ErrorContainer


class UnhandledErrorContainer(ErrorContainer[Exception]):

    def get_error_text(self) -> Text:
        return Text('\n'.join(traceback.format_exception(self.error)))

    def get_default_title(self) -> str:
        return f'Ошибка: {self.error.__class__.__name__}'
