"""
레이아웃 리포지토리
"""

from typing import List, Optional

from app.core.exceptions import LayoutNotFoundError
from app.core.git_env import GitEnv
from app.core.temply.parser.layout_parser import LayoutParser
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User, VersionInfo
from app.models.layout_model import Layout, LayoutCreate, LayoutUpdate


class LayoutRepository:
    """레이아웃 리포지토리"""

    def __init__(
        self,
        version_info: VersionInfo,
        temply_env: TemplyEnv,
        git_env: Optional[GitEnv] = None,
    ):
        """초기화"""
        self.version_info = version_info
        self.temply_env = temply_env
        self.layout_parser = LayoutParser(self.temply_env)
        self.git_env = git_env

    async def create(self, user: User, layout_create: LayoutCreate) -> Layout:

        if self.version_info.is_root:
            raise ValueError("Root version cannot be created")

        """레이아웃 생성"""
        layout = await self.layout_parser.create(
            user, layout_create.name, layout_create.content, layout_create.description
        )
        if self.git_env:
            self.git_env.commit_version(
                user,
                f"Create layout {layout_create.name}",
                [f"{self.temply_env.build_layout_path(layout_create.name)}"],
            )
        return Layout.model_validate(layout)

    async def get(self, layout_name: str) -> Layout:
        """레이아웃 조회"""
        layout = await self.layout_parser.get_layout(layout_name)
        if layout is None:
            raise LayoutNotFoundError(f"Layout {layout_name} not found")
        return Layout.model_validate(layout)

    async def update(self, user: User, layout_name: str, layout_update: LayoutUpdate) -> Layout:
        """레이아웃 수정"""
        if self.version_info.is_root:
            raise ValueError("Root version cannot be updated")
        layout = await self.layout_parser.update(
            user, layout_name, layout_update.content, layout_update.description
        )
        if self.git_env:
            self.git_env.commit_version(
                user,
                f"Update layout {layout_name}",
                [f"{self.temply_env.build_layout_path(layout_name)}"],
            )
        return Layout.model_validate(layout)

    async def delete(self, user: User, layout_name: str) -> None:
        if self.version_info.is_root:
            raise ValueError("Root version cannot be deleted")

        """레이아웃 삭제"""
        await self.layout_parser.delete(user, layout_name)

        if self.git_env:
            self.git_env.commit_version(
                user,
                f"Delete layout {layout_name}",
                [f"{self.temply_env.build_layout_path(layout_name)}"],
            )

    async def list(self) -> List[Layout]:
        """레이아웃 목록 조회"""
        layouts = await self.layout_parser.get_layouts()
        return [Layout.model_validate(layout) for layout in layouts]
