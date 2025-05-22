import re

from fastapi import Depends, HTTPException, Path

from app.core.config import CONFIG
from app.core.temply.temply_env import TemplyEnv
from app.core.temply_version_env import TemplyVersionEnv
from app.models.common_model import User
from app.repositories.layout_repository import LayoutRepository
from app.repositories.partial_repository import PartialRepository
from app.repositories.template_repository import TemplateRepository
from app.services.layout_service import LayoutService
from app.services.partial_service import PartialService
from app.services.template_service import TemplateService


def get_user() -> User:
    """Get User"""
    return User(name="admin")


version_pattern = re.compile(r"^r\d+(?:_pr\d+)?$")

# TODO 버전 별 env 관리가 필요
# env_list[version] = TemplyEnv


def get_temply_env(
    version: str = Path(
        ...,
        example="root",
        description="Version or revision (e.g., 'r1', 'r1_pr123', 'root')",
    )
) -> TemplyEnv:
    """Get Temply Env with version

    Args:
        version (str): Version or revision (e.g., 'r1', 'r1_pr123', 'root')
    """
    if not version:
        raise HTTPException(status_code=400, detail="Invalid version or revision")
    if version == "root":
        return TemplyEnv(CONFIG, "root")
    if not version_pattern.match(version):
        raise HTTPException(status_code=400, detail="Invalid version format")

    # 버전이 검증된 후에 분리
    parts = version.split("_pr")
    base_version = parts[0]
    pr_number = f"pr{parts[1]}" if len(parts) > 1 else None

    return TemplyVersionEnv(CONFIG, base_version, pr_number).get_temply_env()


def get_default_temply_env() -> TemplyEnv:
    """Get Default Temply Env (root version)"""
    return TemplyEnv(CONFIG, "root")


def get_partial_service(temply_env: TemplyEnv = Depends(get_temply_env)):
    """Get Partial Service"""
    return PartialService(PartialRepository(temply_env))


def get_layout_service(temply_env: TemplyEnv = Depends(get_temply_env)):
    """Get Layout Service"""
    return LayoutService(LayoutRepository(temply_env))


def get_template_service(temply_env: TemplyEnv = Depends(get_temply_env)):
    """Get Template Service"""
    return TemplateService(TemplateRepository(temply_env))
