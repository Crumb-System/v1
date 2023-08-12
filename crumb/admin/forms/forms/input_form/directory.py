from flet import Row

from crumb.entities.directories import DirectoryRepository

from .model import ModelInputForm


class DirectoryInputForm(ModelInputForm[DirectoryRepository]):
    def get_action_bar(self) -> Row:
        action_bar = super().get_action_bar()
        action_bar.controls.append(self.save_btn())
        return action_bar

