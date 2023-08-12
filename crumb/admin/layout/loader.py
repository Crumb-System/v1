from flet import Container, Column, Text


class Loader(Container):
    def __init__(self):
        super().__init__()
        self.content = Column([Text('Загрузка...', size=40)])
