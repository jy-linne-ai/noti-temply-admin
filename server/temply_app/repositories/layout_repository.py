"""
레이아웃 리포지토리
"""

from typing import List

from temply_app.core.exceptions import LayoutNotFoundError
from temply_app.core.git_env import GitEnv
from temply_app.core.temply.parser.layout_parser import LayoutParser
from temply_app.core.temply.parser.template_parser import TemplateParser
from temply_app.core.temply.temply_env import TemplyEnv
from temply_app.core.utils.cache_util import get_layout_parser, get_template_parser
from temply_app.core.utils.git_util import GitUtil
from temply_app.models.common_model import User, VersionInfo
from temply_app.models.layout_model import Layout, LayoutCreate, LayoutUpdate


class LayoutRepository:
    """레이아웃 리포지토리"""

    def __init__(
        self,
        version_info: VersionInfo,
        temply_env: TemplyEnv,
        git_env: GitEnv | None = None,
    ):
        """초기화"""
        self.version_info = version_info
        self.temply_env = temply_env
        self.layout_parser: LayoutParser = get_layout_parser(self.temply_env)
        self.template_parser: TemplateParser = get_template_parser(self.temply_env)

        self.git_env: GitEnv | None = git_env

    async def create(self, user: User, layout_create: LayoutCreate) -> Layout:

        if self.version_info.is_root:
            raise ValueError("Root version cannot be created")

        """레이아웃 생성"""
        layout = await self.layout_parser.create(
            user, layout_create.name, layout_create.content, layout_create.description
        )
        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
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

    async def update(
        self, user: User, layout_name: str, layout_update: LayoutUpdate
    ) -> tuple[Layout, List[str]]:
        """레이아웃 수정"""
        if self.version_info.is_root:
            raise ValueError("Root version cannot be updated")
        layout = await self.layout_parser.update(
            user, layout_name, layout_update.content, layout_update.description
        )
        components = await self.template_parser.get_components_using_layout(layout_name)
        template_names = set([component.template for component in components])
        updated_template_files = []
        for template_name in template_names:
            updated_file = await self.template_parser.sync_schema(template_name)
            if updated_file:
                updated_template_files.append(updated_file)
        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
                user,
                f"Update layout {layout_name}",
                [f"{self.temply_env.build_layout_path(layout_name)}"] + updated_template_files,
            )
        return Layout.model_validate(layout), updated_template_files

    async def delete(self, user: User, layout_name: str) -> None:
        """레이아웃 삭제"""
        if self.version_info.is_root:
            raise ValueError("Root version cannot be deleted")
        components = await self.template_parser.get_components_using_layout(layout_name)
        if len(components) > 0:
            raise ValueError("Layout is used by components")
        await self.layout_parser.delete(user, layout_name)

        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
                user,
                f"Delete layout {layout_name}",
                [f"{self.temply_env.build_layout_path(layout_name)}"],
            )

    async def list(self) -> List[Layout]:
        """레이아웃 목록 조회"""
        layouts = await self.layout_parser.get_layouts()
        return [Layout.model_validate(layout) for layout in layouts]
