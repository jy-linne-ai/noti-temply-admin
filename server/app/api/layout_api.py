from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.dependency import get_layout_service, get_user
from app.core.exceptions import LayoutAlreadyExistsError, LayoutNotFoundError
from app.models.common_model import User
from app.models.layout_model import Layout, LayoutCreate, LayoutUpdate
from app.services.layout_service import LayoutService

router = APIRouter(
    prefix="/layouts",
    tags=["layouts"],
)


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


@router.get("/{layout}", response_model=Layout)
async def get_layout(
    layout: str,
    layout_service: LayoutService = Depends(get_layout_service),
    user: User = Depends(get_user),
) -> Layout:
    """레이아웃 조회"""
    try:
        return await layout_service.get(layout)
    except LayoutNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("", response_model=List[Layout])
async def list_layouts(
    layout_service: LayoutService = Depends(get_layout_service),
    user: User = Depends(get_user),
) -> List[Layout]:
    """레이아웃 목록 조회"""
    return await layout_service.list()


@router.put("/{layout}", response_model=Layout)
async def update_layout(
    layout: str,
    layout_update: LayoutUpdate,
    layout_service: LayoutService = Depends(get_layout_service),
    user: User = Depends(get_user),
) -> Layout:
    """레이아웃 수정"""
    try:
        return await layout_service.update(user, layout, layout_update)
    except LayoutNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{layout}")
async def delete_layout(
    layout: str,
    layout_service: LayoutService = Depends(get_layout_service),
    user: User = Depends(get_user),
) -> JSONResponse:
    """레이아웃 삭제"""
    try:
        await layout_service.delete(user, layout)
        return JSONResponse(status_code=204, content={"message": "Layout deleted successfully"})
    except LayoutNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
