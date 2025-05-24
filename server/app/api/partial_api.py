"""Partial API"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.dependency import get_partial_service, get_user
from app.core.exceptions import (
    PartialAlreadyExistsError,
    PartialCircularDependencyError,
    PartialNotFoundError,
)
from app.models.common_model import User
from app.models.partial_model import Partial, PartialCreate, PartialUpdate
from app.services.partial_service import PartialService

router = APIRouter()


@router.get("", response_model=List[Partial])
async def list_partials(
    is_root: bool = False,
    partial_service: PartialService = Depends(get_partial_service),
    user: User = Depends(get_user),
) -> List[Partial]:
    """파셜 목록을 조회합니다.

    Args:
        is_root: 루트 파셜만 조회할지 여부
    """
    if is_root:
        return await partial_service.get_root()
    return await partial_service.list()


@router.get("/{partial}")
async def get_partial(
    partial: str,
    partial_service: PartialService = Depends(get_partial_service),
    user: User = Depends(get_user),
) -> Partial:
    """파셜 정보를 조회합니다."""
    try:
        return await partial_service.get(partial)
    except PartialNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("")
async def create_partial(
    partial_create: PartialCreate,
    partial_service: PartialService = Depends(get_partial_service),
    user: User = Depends(get_user),
) -> Partial:
    """새로운 파셜을 생성합니다."""
    try:
        return await partial_service.create(user, partial_create)
    except PartialAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except PartialCircularDependencyError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{partial}")
async def update_partial(
    partial: str,
    partial_update: PartialUpdate,
    partial_service: PartialService = Depends(get_partial_service),
    user: User = Depends(get_user),
) -> Partial:
    """파셜을 수정합니다."""
    try:
        return await partial_service.update(user, partial, partial_update)
    except PartialNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except PartialCircularDependencyError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{partial}")
async def delete_partial(
    partial: str,
    partial_service: PartialService = Depends(get_partial_service),
    user: User = Depends(get_user),
) -> JSONResponse:
    """파셜을 삭제합니다."""
    try:
        await partial_service.delete(user, partial)
        return JSONResponse(status_code=204, content={"message": "Partial deleted successfully"})
    except PartialNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{partial}/children", response_model=List[Partial])
async def get_child_partials(
    partial: str,
    partial_service: PartialService = Depends(get_partial_service),
    user: User = Depends(get_user),
) -> List[Partial]:
    """자식 파셜 목록을 조회합니다."""
    try:
        return await partial_service.get_children(partial)
    except PartialNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{partial}/parents", response_model=List[Partial])
async def get_parent_partials(
    partial: str,
    partial_service: PartialService = Depends(get_partial_service),
    user: User = Depends(get_user),
) -> List[Partial]:
    """부모 파셜 목록을 조회합니다."""
    try:
        return await partial_service.get_parents(partial)
    except PartialNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
