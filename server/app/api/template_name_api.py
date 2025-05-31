"""Template Name API"""

from fastapi import APIRouter, Depends

from app.core.dependency import get_template_service, get_user
from app.models.common_model import User
from app.services.template_service import TemplateService

router = APIRouter()


@router.get("", response_model=dict[str, int])
async def list_template_names(
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> dict[str, int]:
    """Get template names with component counts"""
    return await template_service.get_template_component_counts()
