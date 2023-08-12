from enum import Enum
from typing import TYPE_CHECKING, Type, TypeVar

from .entity import EntityTranslation
from .interface import InterfaceTranslation

if TYPE_CHECKING:
    from ..repository import Repository


E = TypeVar('E', bound=Enum)


class AppTranslation:

    def __init__(
            self,
            default: str = 'ru',
            **languages: InterfaceTranslation
    ):
        self.default = default
        self.languages = languages
        assert self.default in self.languages

    def add_repository(self, repo: "Repository") -> None:
        repo_languages = {}
        for lang in self.languages:
            repo_lang: EntityTranslation = getattr(repo, f'_t_{lang}', None)
            if repo_lang is None:
                raise ValueError(f'{repo} не имеет перевода для языка {lang}')
            repo_languages[lang] = repo_lang
        for lang_name, translation in repo_languages.items():
            self.languages[lang_name].add_entity(repo.entity(), translation)

    def get(self, lang: str) -> InterfaceTranslation:
        return self.languages[lang]

    def add_enum(self, enum_type: Type[E], **languages: dict[E, str]) -> None:
        assert len(self.languages) == len(languages)
        assert all(lang in languages for lang in self.languages)
        for lang, translation in languages.items():
            assert len(enum_type.__members__) == len(translation)
            assert all(m in translation for m in enum_type.__members__.values())
            self.languages[lang].add_enum(enum_type, translation)
