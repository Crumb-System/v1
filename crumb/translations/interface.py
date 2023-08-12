from dataclasses import dataclass, field
from enum import Enum
from typing import Type

from .entity import EntityTranslation


@dataclass
class InterfaceTranslation:
    __lang__: str
    settings: str
    sign_in: str
    sign_out: str

    common_fields: dict[str, str]
    entities: dict[str, EntityTranslation] = field(default_factory=dict)
    enums: dict[Type[Enum], dict[Enum, str]] = field(default_factory=dict)

    def add_common_fields(self, **fields: str):
        self.common_fields.update(**fields)

    def add_entity(self, name: str, translation: EntityTranslation):
        self.entities[name] = translation
        translation.interface = self

    def translate(self, key: str):
        res = getattr(self, key, None)
        if res is None:
            raise KeyError(f'Нет перевода для {key}')
        return res

    def get_entity(self, name: str):
        return self.entities[name]

    def add_enum(self, enum_type: Type[Enum], translates: dict[Enum, str]):
        self.enums[enum_type] = translates

    def get_enum_translations(self, enum_type: Type[Enum]):
        return self.enums[enum_type]
