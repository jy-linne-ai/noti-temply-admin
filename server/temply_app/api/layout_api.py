"""Layout API"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from temply_app.core.dependency import get_layout_service, get_template_service, get_user
from temply_app.core.exceptions import LayoutAlreadyExistsError, LayoutNotFoundError
from temply_app.models.common_model import User
from temply_app.models.layout_model import Layout, LayoutCreate, LayoutUpdate, LayoutUpdateResponse
from temply_app.models.template_model import TemplateComponent
from temply_app.services.layout_service import LayoutService
from temply_app.services.template_service import TemplateService

router = APIRouter()


@router.get("", response_model=List[Layout])
async def list_layouts(
    layout_service: LayoutService = Depends(get_layout_service),
    user: User = Depends(get_user),
) -> List[Layout]:
    """레이아웃 목록 조회"""
    return await layout_service.list()


@router.post("", response_model=Layout)
async def create_layout(
    layout_create: LayoutCreate,
    layout_service: LayoutService = Depends(get_layout_service),
    user: User = Depends(get_user),
) -> Layout:
    """레이아웃 생성"""
    try:
        return await layout_service.create(user, layout_create)
    except LayoutAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{layout_name}", response_model=Layout)
async def get_layout(
    layout_name: str,
    layout_service: LayoutService = Depends(get_layout_service),
    user: User = Depends(get_user),
) -> Layout:
    """레이아웃 조회"""
    try:
        return await layout_service.get(layout_name)
    except LayoutNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{layout_name}/templates", response_model=List[TemplateComponent])
async def get_layout_templates(
    layout_name: str,
    layout_service: LayoutService = Depends(get_layout_service),
    template_service: TemplateService = Depends(get_template_service),
    user: User = Depends(get_user),
) -> List[TemplateComponent]:
    """레이아웃 조회"""
    try:
        layout = await layout_service.get(layout_name)
        if layout is None:
            raise LayoutNotFoundError(f"Layout {layout_name} not found")
        return await template_service.get_components_by_layout(layout_name)
    except LayoutNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.put("/{layout_name}", response_model=LayoutUpdateResponse)
async def update_layout(
    layout_name: str,
    layout_update: LayoutUpdate,
    layout_service: LayoutService = Depends(get_layout_service),
    user: User = Depends(get_user),
) -> LayoutUpdateResponse:
    """레이아웃 수정"""
    try:
        layout, updated_template_files = await layout_service.update(
            user, layout_name, layout_update
        )
        return LayoutUpdateResponse(
            **layout.model_dump(),
            updated_template_files=updated_template_files,
        )
    except LayoutNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{layout_name}")
async def delete_layout(
    layout_name: str,
    layout_service: LayoutService = Depends(get_layout_service),
    user: User = Depends(get_user),
) -> Response:
    """레이아웃 삭제"""
    try:
        await layout_service.delete(user, layout_name)
        return Response(status_code=204)
    except LayoutNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
