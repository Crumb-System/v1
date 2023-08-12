from flet import Row, ElevatedButton

from crumb.entities.documents import DocumentRepository
from crumb.enums import NotifyStatus

from .model import ModelInputForm


class DocumentInputForm(ModelInputForm[DocumentRepository]):

    def get_widget_creator(self):
        widget_creator = super().get_widget_creator()
        if self.instance and self.instance.conducted:
            widget_creator.all_read_only = True
        return widget_creator

    async def conduct(self):
        instance, created = await self.save()
        if instance is None:
            return
        await self.repository(instance=instance).conduct()
        if created:
            await self.app.notify(f'{instance} создан и проведен', NotifyStatus.SUCCESS)
            await self.on_success(form=self, instance=instance)
        else:
            await self.app.notify(f'{instance} сохранён и проведен', NotifyStatus.SUCCESS)
            await self.on_success(form=self, instance=instance)

    async def on_click_conduct(self, e=None):
        async with self.app.error_tracker():
            await self.conduct()

    async def unconduct(self):
        await self.repository(instance=self.instance).unconduct()
        await self.app.notify(f'Проведение {self.instance} отменено', NotifyStatus.SUCCESS)
        await self.box.reload_content()

    async def on_click_unconduct(self, e=None):
        async with self.app.error_tracker():
            await self.unconduct()

    def get_action_bar(self) -> Row:
        action_bar = super().get_action_bar()
        if self.instance and self.instance.conducted:
            action_bar.controls.append(ElevatedButton('Отменить проведение', on_click=self.on_click_unconduct))
        else:
            action_bar.controls.extend((
                self.save_btn(),
                ElevatedButton(
                    'Создать и провести' if self.create else 'Сохранить и провести',
                    on_click=self.on_click_conduct
                )
            ))
        return action_bar
