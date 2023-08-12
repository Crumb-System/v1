from typing import TYPE_CHECKING

from flet import UserControl, Column, Control, Row

if TYPE_CHECKING:
    from crumb.admin.layout import BOX


class Form(UserControl):
    body: Control
    action_bar: Row

    def __init__(
            self,
            box: "BOX",
    ):
        UserControl.__init__(self)
        self.box = box

    def build(self):
        controls = []
        self.body = self.build_body()
        self.action_bar: Row = self.get_action_bar()
        if self.action_bar.controls:
            controls.append(self.action_bar)
        controls.append(self.body)
        return Column(controls=controls, spacing=10)

    def build_body(self) -> Control:
        raise NotImplementedError

    def get_action_bar(self) -> Row:
        raise NotImplementedError
