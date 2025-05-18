"""
레이아웃 리포지토리
"""

from app.core.temply.parser.layout_parser import LayoutParser
from app.core.temply.parser.meta_model import BaseMetaData
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

        meta = BaseMetaData(
            description=layout.description,
            created_at=BaseMetaData.get_current_datetime(),
            created_by=user.name,
            updated_at=BaseMetaData.get_current_datetime(),
            updated_by=user.name,
        )

        layout = await self.layout_parser.create(layout.name, layout.content, meta)
        return Layout.model_validate(layout)

    async def get(self, name: str) -> Layout:
        """레이아웃 조회"""
        layout = await self.layout_parser.get_layout(name)
        return Layout.model_validate(layout)

    async def update(self, user: User, name: str, layout: LayoutUpdate) -> Layout:
        """레이아웃 수정"""
        meta = BaseMetaData(
            description=layout.description,
            updated_at=BaseMetaData.get_current_datetime(),
            updated_by=user.name,
        )
        layout = await self.layout_parser.update(name, layout.content, meta)
        return Layout.model_validate(layout)

    async def delete(self, name: str) -> None:
        """레이아웃 삭제"""
        await self.layout_parser.delete(name)
