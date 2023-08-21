from dataclasses import dataclass

from ..entity import EntityTranslation
from ..interface import InterfaceTranslation


__all__ = ["interface", "Entity"]


interface = InterfaceTranslation(
    __lang__='English',
    settings='Settings',
    sign_in='Sign in',
    sign_out='Sign out',
    common_fields={
        'name': 'Name',
        'ordering': '№',
        'count': 'Count',
        'price': 'Price',
        'dt': 'Date and time',
        'date': 'Date',
        'time': 'Time',
        'comment': 'Comment',
        'registrator': 'Registrator',
        'responsible': 'Responsible',
        'unique_number': 'Number',
        'type': 'Type',
    },
)


@dataclass
class Entity(EntityTranslation):
    _list: str = 'List'
    _choice: str = 'Choice'
    _creation: str = 'Creation'
