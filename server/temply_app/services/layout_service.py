"""
레이아웃 서비스
"""

from typing import List

from temply_app.models.common_model import User
from temply_app.models.layout_model import Layout, LayoutCreate, LayoutUpdate
from temply_app.repositories.layout_repository import LayoutRepository


class LayoutService:
    """레이아웃 관련 기능을 제공하는 서비스"""

    def __init__(self, repository: LayoutRepository):
        """서비스 초기화"""
        self.repository = repository

    async def create(self, user: User, layout_create: LayoutCreate) -> Layout:
        """레이아웃 생성"""
        return await self.repository.create(user, layout_create)

    async def get(self, layout_name: str) -> Layout:
        """레이아웃 조회"""
        return await self.repository.get(layout_name)

    async def list(self) -> List[Layout]:
        """레이아웃 목록 조회"""
        return await self.repository.list()

    async def update(self, user: User, layout_name: str, layout_update: LayoutUpdate) -> Layout:
        """레이아웃 수정"""
        return await self.repository.update(user, layout_name, layout_update)

    async def delete(self, user: User, layout_name: str) -> None:
        """레이아웃 삭제"""
        return await self.repository.delete(user, layout_name)
