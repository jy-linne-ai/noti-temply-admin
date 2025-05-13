from typing import Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException

from ..services.partial import PartialService

router = APIRouter(
    prefix="/partials",
    tags=["partials"],
)

partial_service = PartialService()

@router.get("")
async def list_partials(
    parent_id: Optional[str] = None,
) -> List[Dict]:
    """파셜 목록을 조회합니다."""
    return partial_service.list_partials(parent_id=parent_id)

@router.get("/{partial_id}")
async def get_partial(
    partial_id: str,
) -> Dict:
    """파셜 정보를 조회합니다."""
    partial = partial_service.get_partial(partial_id)
    if not partial:
        raise HTTPException(status_code=404, detail="파셜을 찾을 수 없습니다.")
    return partial

@router.post("")
async def create_partial(
    partial_id: str,
    info: Dict,
    schema_data: Dict,
    content: str,
) -> Dict:
    """새로운 파셜을 생성합니다."""
    # 메타데이터 추가
    info.update({
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    })

    success = partial_service.create_partial(
        partial_id, info, schema_data, content
    )
    if not success:
        raise HTTPException(status_code=400, detail="파셜 생성에 실패했습니다.")

    return partial_service.get_partial(partial_id)

@router.put("/{partial_id}")
async def update_partial(
    partial_id: str,
    info: Dict,
    schema_data: Dict,
    content: str,
) -> Dict:
    """파셜을 수정합니다."""
    # 메타데이터 업데이트
    info.update({
        "updated_at": datetime.now().isoformat(),
    })

    success = partial_service.update_partial(
        partial_id, info, schema_data, content
    )
    if not success:
        raise HTTPException(status_code=404, detail="파셜을 찾을 수 없습니다.")

    return partial_service.get_partial(partial_id)

@router.delete("/{partial_id}")
async def delete_partial(
    partial_id: str,
) -> Dict:
    """파셜을 삭제합니다."""
    success = partial_service.delete_partial(partial_id)
    if not success:
        raise HTTPException(status_code=404, detail="파셜을 찾을 수 없습니다.")
    return {"message": "파셜이 삭제되었습니다."} 