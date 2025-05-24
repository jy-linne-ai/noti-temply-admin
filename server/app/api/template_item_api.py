"""Template Item API"""

from typing import List

from fastapi import APIRouter

from app.core.temply.temply_env import TemplateItems

router = APIRouter()


@router.get("", response_model=List[str])
async def list_template_item_types() -> List[str]:
    """템플릿 아이템 타입 목록을 조회합니다."""
    return [item_type.value for item_type in TemplateItems]
