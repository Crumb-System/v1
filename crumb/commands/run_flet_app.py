from crumb.commands import Command, register_command
from crumb.utils import get_settings, import_string


@register_command
class RunFletApp(Command):
    name = 'flet'
    need_db_connection = False

    def handle(self):
        import_string(get_settings().FLET_APP).run_app()
