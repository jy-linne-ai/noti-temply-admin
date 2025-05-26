from fastapi import Depends, HTTPException, Path

from app.core.config import CONFIG, Config
from app.core.git_env import GitEnv
from app.core.temply.temply_env import TemplyEnv
from app.core.temply_version_env import TemplyVersionEnv
from app.models.common_model import User, VersionInfo
from app.repositories.layout_repository import LayoutRepository
from app.repositories.partial_repository import PartialRepository
from app.repositories.template_repository import TemplateRepository
from app.services.layout_service import LayoutService
from app.services.partial_service import PartialService
from app.services.template_service import TemplateService


def get_user() -> User:
    """Get User"""
    return User(name="admin")


# TODO 버전 별 env 관리가 필요
# env_list[version] = TemplyEnv


def get_config() -> Config:
    """Get Config"""
    return CONFIG


def get_version_info(
    version: str = Path(
        ...,
        example="main",
        description="Version or revision (e.g., 'r1', 'r1_pr123', 'main')",
    ),
    config: Config = Depends(get_config),
) -> VersionInfo:
    """Get Version Info"""
    try:
        return VersionInfo(config, version)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def get_temply_env(
    version_info: VersionInfo = Depends(get_version_info),
) -> TemplyEnv:
    """Get Temply Env"""
    # cache ??
    return TemplyVersionEnv(version_info.config, version_info).get_temply_env()


def get_git_env(
    version_info: VersionInfo = Depends(get_version_info),
) -> GitEnv:
    """Get Git Env"""
    return GitEnv(version_info)


def get_layout_service(
    version_info: VersionInfo = Depends(get_version_info),
    temply_env: TemplyEnv = Depends(get_temply_env),
    git_env: GitEnv = Depends(get_git_env),
):
    """Get Layout Service"""
    return LayoutService(LayoutRepository(version_info, temply_env, git_env))


def get_partial_service(
    version_info: VersionInfo = Depends(get_version_info),
    temply_env: TemplyEnv = Depends(get_temply_env),
    git_env: GitEnv = Depends(get_git_env),
):
    """Get Partial Service"""
    return PartialService(PartialRepository(version_info, temply_env, git_env))


def get_template_service(
    version_info: VersionInfo = Depends(get_version_info),
    temply_env: TemplyEnv = Depends(get_temply_env),
    git_env: GitEnv = Depends(get_git_env),
):
    """Get Template Service"""
    return TemplateService(TemplateRepository(version_info, temply_env, git_env))
