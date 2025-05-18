from fastapi import Depends

from app.core.config import CONFIG
from app.core.temply.temply_env import TemplyEnv
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


def get_temply_env() -> TemplyEnv:
    """Get Temply Env"""
    return TemplyEnv(CONFIG)


def get_partial_service(temply_env: TemplyEnv = Depends(get_temply_env)):
    """Get Partial Service"""
    return PartialService(PartialRepository(temply_env))


def get_layout_service(temply_env: TemplyEnv = Depends(get_temply_env)):
    """Get Layout Service"""
    return LayoutService(LayoutRepository(temply_env))


def get_template_service(temply_env: TemplyEnv = Depends(get_temply_env)):
    """Get Template Service"""
    return TemplateService(TemplateRepository(temply_env))
