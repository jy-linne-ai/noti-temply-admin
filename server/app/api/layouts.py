from typing import Dict, List

from fastapi import APIRouter, HTTPException

from ..services.layout import LayoutService

router = APIRouter(prefix="/api/layouts", tags=["layouts"])
layout_service = LayoutService()


@router.get("", response_model=List[Dict])
async def list_layouts():
    """레이아웃 목록을 조회합니다."""
    return layout_service.list_layouts()


@router.get("/{layout_id}", response_model=Dict)
async def get_layout(layout_id: str):
    layout = layout_service.get_layout(layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="레이아웃을 찾을 수 없습니다")
    return layout


@router.post("", response_model=Dict)
async def create_layout(layout_name: str, content: str):
    """레이아웃을 생성합니다."""
    try:
        if layout_service.create_layout(layout_name, content):
            return {"message": "레이아웃이 생성되었습니다"}
        raise HTTPException(status_code=400, detail="레이아웃 생성에 실패했습니다")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{layout_id}", response_model=Dict)
async def update_layout(layout_id: str, info: Dict, schema: Dict, layout: str):
    """레이아웃을 수정합니다."""
    if layout_service.update_layout(layout_id, info, schema, layout):
        return {"message": "레이아웃이 수정되었습니다"}
    raise HTTPException(status_code=404, detail="레이아웃을 찾을 수 없습니다")


@router.delete("/{layout_id}")
async def delete_layout(layout_id: str):
    """레이아웃을 삭제합니다."""
    if not layout_service.delete_layout(layout_id):
        raise HTTPException(status_code=404, detail="레이아웃을 찾을 수 없습니다")
    return {"message": "레이아웃이 삭제되었습니다"}
