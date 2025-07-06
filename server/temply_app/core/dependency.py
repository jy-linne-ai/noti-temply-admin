import os
import threading
from typing import Optional

from fastapi import Depends, HTTPException, Path

from temply_app.core.config import Config
from temply_app.core.git_env import GitEnv
from temply_app.core.temply.temply_env import TemplyEnv
from temply_app.core.temply_version_env import TemplyVersionEnv
from temply_app.models.common_model import User, VersionInfo
from temply_app.repositories.layout_repository import LayoutRepository
from temply_app.repositories.partial_repository import PartialRepository
from temply_app.repositories.template_repository import TemplateRepository
from temply_app.services.layout_service import LayoutService
from temply_app.services.partial_service import PartialService
from temply_app.services.template_service import TemplateService


def get_user() -> User:
    """Get User"""
    return User(name="admin")


# TODO 버전 별 env 관리가 필요
# env_list[version] = TemplyEnv

_config: Optional[Config] = None
_config_lock = threading.Lock()


def get_config() -> Config:
    """Get Config in a thread-safe manner"""
    global _config  # pylint: disable=global-statement
    if _config is None:
        with _config_lock:
            # Double-checked locking pattern
            if _config is None:
                _config = Config()
    return _config


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


def get_git_env(
    config: Config = Depends(get_config),
    version_info: VersionInfo = Depends(get_version_info),
) -> GitEnv | None:
    """Get Git Env"""
    if not config.is_git_used():
        return None
    return GitEnv(config, version_info)


def get_temply_env(
    config: Config = Depends(get_config),
    version_info: VersionInfo = Depends(get_version_info),
    git_env: GitEnv | None = Depends(get_git_env),
) -> TemplyEnv:
    """Get Temply Env"""
    return TemplyVersionEnv(config, version_info, git_env).get_temply_env()


def get_layout_service(
    version_info: VersionInfo = Depends(get_version_info),
    temply_env: TemplyEnv = Depends(get_temply_env),
):
    """Get Layout Service"""
    return LayoutService(LayoutRepository(version_info, temply_env))


def get_partial_service(
    version_info: VersionInfo = Depends(get_version_info),
    temply_env: TemplyEnv = Depends(get_temply_env),
):
    """Get Partial Service"""
    return PartialService(PartialRepository(version_info, temply_env))


def get_template_service(
    version_info: VersionInfo = Depends(get_version_info),
    temply_env: TemplyEnv = Depends(get_temply_env),
):
    """Get Template Service"""
    return TemplateService(TemplateRepository(version_info, temply_env))
