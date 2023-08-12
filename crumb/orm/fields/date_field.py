from tortoise import fields


class DateField(fields.DateField):
    def __init__(self, editable: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.editable = editable

    @property
    def constraints(self) -> dict:
        return {
            'editable': self.editable
        }
