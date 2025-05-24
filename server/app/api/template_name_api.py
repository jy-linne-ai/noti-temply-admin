"""Template Name API"""

from typing import List

from fastapi import APIRouter, Depends

from app.core.dependency import get_template_service, get_user
from app.models.common_model import User
from app.services.template_service import TemplateService

router = APIRouter()


@router.get("", response_model=List[str])
async def list_template_names(
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> List[str]:
    """템플릿 이름 목록을 조회합니다."""
    return await template_service.get_template_names()
