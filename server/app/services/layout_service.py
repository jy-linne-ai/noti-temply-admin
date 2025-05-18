"""
레이아웃 서비스
"""

from datetime import datetime
from typing import List, Optional

from app.models.layout_model import Layout, LayoutCreate, LayoutUpdate
from app.repositories.layout_repository import LayoutRepository


class LayoutService:
    """레이아웃 관련 기능을 제공하는 서비스"""

    def __init__(self, repository: LayoutRepository):
        """서비스 초기화"""
        self.repository = repository

    async def create_layout(self, layout: LayoutCreate) -> Layout:
        """레이아웃 생성"""
        layout_data = layout.model_dump()
        layout_data.update(
            {
                "name": layout.name,
                "content": layout.content,
                "description": layout.description,
            }
        )
        return await self.repository.create(layout_data)

    async def get_layout(self, layout_id: str) -> Optional[Layout]:
        """레이아웃 조회"""
        return await self.repository.get(layout_id)

    async def list_layouts(self) -> List[Layout]:
        """레이아웃 목록 조회"""
        return await self.repository.list()

    async def update_layout(self, layout_id: str, layout: LayoutUpdate) -> Optional[Layout]:
        """레이아웃 수정"""
        update_data = layout.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            return await self.repository.update(layout_id, update_data)
        return await self.get_layout(layout_id)

    async def delete_layout(self, layout_id: str) -> bool:
        """레이아웃 삭제"""
        return await self.repository.delete(layout_id)
