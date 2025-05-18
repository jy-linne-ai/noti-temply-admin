"""Template API"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.dependency import get_template_service, get_user
from app.core.exceptions import TemplateAlreadyExistsError, TemplateNotFoundError
from app.models.common_model import User
from app.models.template_model import Template, TemplateCreate, TemplateUpdate
from app.services.template_service import TemplateService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[str])
async def list_categories(
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> List[str]:
    """카테고리 목록을 조회합니다."""
    return await template_service.get_categories()


@router.post("/{category}/templates", response_model=Template)
async def create_template(
    category: str,
    template_create: TemplateCreate,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> Template:
    """새로운 템플릿을 생성합니다."""
    try:
        return await template_service.create(user, category, template_create)
    except TemplateAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{category}/templates", response_model=List[Template])
async def list_templates_by_category(
    category: str,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> List[Template]:
    """특정 카테고리의 템플릿 목록을 조회합니다."""
    return await template_service.get_templates(category)


@router.delete("/{category}/templates", response_model=List[str])
async def delete_templates_by_category(
    category: str,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> List[str]:
    """특정 카테고리의 템플릿을 삭제합니다."""
    try:
        await template_service.delete_templates(user, category)
        return JSONResponse(status_code=204, content={"message": "Templates deleted successfully"})
    except TemplateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{category}/templates/{template_name}", response_model=Template)
async def get_template(
    category: str,
    template_name: str,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> List[Template]:
    """특정 카테고리의 특정 타입 템플릿 목록을 조회합니다."""
    try:
        return await template_service.get(category, template_name)
    except TemplateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.put("/{category}/templates/{template_name}", response_model=Template)
async def update_template(
    category: str,
    template_name: str,
    template_update: TemplateUpdate,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> Template:
    """템플릿을 수정합니다."""
    try:
        return await template_service.update(user, category, template_name, template_update)
    except TemplateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{category}/templates/{template_name}")
async def delete_template(
    category: str,
    template_name: str,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> JSONResponse:
    """템플릿을 삭제합니다."""
    try:
        await template_service.delete(user, category, template_name)
        return JSONResponse(status_code=204, content={"message": "Template deleted successfully"})
    except TemplateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
