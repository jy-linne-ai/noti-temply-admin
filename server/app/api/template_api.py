"""Template API"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.dependency import get_template_service, get_user
from app.core.exceptions import TemplateAlreadyExistsError, TemplateNotFoundError
from app.models.common_model import User
from app.models.template_model import (
    TemplateComponent,
    TemplateComponentCreate,
    TemplateComponentUpdate,
)
from app.services.template_service import TemplateService

router = APIRouter()


@router.get("", response_model=List[TemplateComponent])
async def list_templates(
    layout: Optional[str] = None,
    partial: Optional[str] = None,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> List[TemplateComponent]:
    """카테고리 목록을 조회합니다."""
    return await template_service.get_templates()


@router.post("/{template}/components", response_model=TemplateComponent)
async def create_template(
    template: str,
    template_create: TemplateComponentCreate,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> TemplateComponent:
    """새로운 템플릿을 생성합니다."""
    try:
        return await template_service.create_component(user, template, template_create)
    except TemplateAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{template}/components", response_model=List[TemplateComponent])
async def list_templates_by_category(
    template: str,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> List[TemplateComponent]:
    """특정 카테고리의 템플릿 목록을 조회합니다."""
    return await template_service.get_components_by_template(template)


@router.delete("/{template}")
async def delete_template(
    template: str,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> JSONResponse:
    """특정 카테고리의 템플릿을 삭제합니다."""
    try:
        await template_service.delete_components_by_template(user, template)
        return JSONResponse(status_code=204, content={"message": "Components deleted successfully"})
    except TemplateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{template}/components/{component}", response_model=TemplateComponent)
async def get_template_component(
    template: str,
    component: str,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> TemplateComponent:
    """특정 카테고리의 특정 타입 템플릿 목록을 조회합니다."""
    try:
        return await template_service.get_component(template, component)
    except TemplateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.put("/{template}/components/{component}", response_model=TemplateComponent)
async def update_template_component(
    template: str,
    component: str,
    template_update: TemplateComponentUpdate,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> TemplateComponent:
    """템플릿을 수정합니다."""
    try:
        return await template_service.update_component(user, template, component, template_update)
    except TemplateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{template}/components/{component}")
async def delete_template_component(
    template: str,
    component: str,
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> JSONResponse:
    """템플릿을 삭제합니다."""
    try:
        await template_service.delete_component(user, template, component)
        return JSONResponse(status_code=204, content={"message": "Component deleted successfully"})
    except TemplateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
