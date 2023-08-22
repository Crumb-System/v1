from typing import TYPE_CHECKING

from flet import UserControl, Column, Control, Row, Container, ClipBehavior

if TYPE_CHECKING:
    from crumb.admin.layout import BOX


class Form(UserControl):
    body: Control
    action_bar: Row

    def __init__(
            self,
            box: "BOX",
    ):
        UserControl.__init__(self, expand=True)
        self.box = box

    def build(self):
        controls = []
        self.body = self.build_body()
        self.action_bar: Row = self.get_action_bar()
        if self.action_bar.controls:
            controls.append(self.action_bar)
        controls.append(Container(
            self.body,
            expand=True,
            clip_behavior=ClipBehavior.ANTI_ALIAS,
        ))
        return Column(controls=controls, spacing=15)

    def build_body(self) -> Control:
        raise NotImplementedError

    def get_action_bar(self) -> Row:
        raise NotImplementedError
