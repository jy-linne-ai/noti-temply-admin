"""System API"""

from typing import List

from fastapi import APIRouter, Depends

from temply_app.core.config import Config
from temply_app.core.dependency import get_config
from temply_app.core.temply.temply_env import TemplateComponents

router = APIRouter()


@router.get("/git-status", response_model=dict[str, bool])
async def get_git_status(
    config: Config = Depends(get_config),
) -> dict[str, bool]:
    """git 사용 여부 확인"""
    return {"is_git_used": config.is_git_used()}


@router.get("/template-available-components", response_model=List[str])
async def list_template_item_types() -> List[str]:
    """템플릿 아이템 타입 목록을 조회합니다."""
    return [item_type.value for item_type in TemplateComponents]
