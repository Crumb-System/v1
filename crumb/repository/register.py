from crumb.repository.base import REPOSITORY
from crumb.utils import get_app_translations


def register_repository(repo_cls: REPOSITORY) -> REPOSITORY:
    if not hasattr(repo_cls.model, 'REPOSITORIES'):
        repo_cls.model.REPOSITORIES = {}
    repo_name = repo_cls.get_repo_name()
    if repo_name in repo_cls.model.REPOSITORIES:
        raise ValueError(f'{repo_cls.model} уже имеет репозиторий с именем {repo_name}')
    repo_cls.model.REPOSITORIES[repo_name] = repo_cls
    get_app_translations().add_repository(repo_cls)
    return repo_cls
