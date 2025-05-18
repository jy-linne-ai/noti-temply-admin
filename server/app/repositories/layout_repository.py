"""
레이아웃 리포지토리
"""

from typing import List

from app.core.temply.parser.layout_parser import LayoutParser
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User
from app.models.layout_model import Layout, LayoutCreate, LayoutUpdate


class LayoutRepository:
    """레이아웃 리포지토리"""

    def __init__(self, temply_env: TemplyEnv):
        """초기화"""
        self.temply_env = temply_env
        self.layout_parser = LayoutParser(self.temply_env)

    async def create(self, user: User, layout: LayoutCreate) -> Layout:
        """레이아웃 생성"""
        layout = await self.layout_parser.create(
            user, layout.name, layout.content, layout.description
        )
        return Layout.model_validate(layout)

    async def get(self, layout_name: str) -> Layout:
        """레이아웃 조회"""
        layout = await self.layout_parser.get_layout(layout_name)
        return Layout.model_validate(layout)

    async def update(self, user: User, layout_name: str, layout: LayoutUpdate) -> Layout:
        """레이아웃 수정"""
        layout = await self.layout_parser.update(
            user, layout_name, layout.content, layout.description
        )
        return Layout.model_validate(layout)

    async def delete(self, user: User, layout_name: str) -> None:
        """레이아웃 삭제"""
        await self.layout_parser.delete(user, layout_name)

    async def list(self) -> List[Layout]:
        """레이아웃 목록 조회"""
        layouts = await self.layout_parser.get_layouts()
        return [Layout.model_validate(layout) for layout in layouts]
