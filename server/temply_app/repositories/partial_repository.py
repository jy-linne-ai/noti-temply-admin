"""Partial Repository"""

from typing import List

from temply_app.core.git_env import GitEnv
from temply_app.core.temply.parser.partial_parser import PartialParser
from temply_app.core.temply.parser.template_parser import TemplateParser
from temply_app.core.temply.temply_env import TemplyEnv
from temply_app.core.utils.cache_util import get_partial_parser, get_template_parser
from temply_app.core.utils.git_util import GitUtil
from temply_app.models.common_model import User, VersionInfo
from temply_app.models.partial_model import Partial, PartialCreate, PartialUpdate


class PartialRepository:
    """Partial Repository"""

    def __init__(
        self,
        version_info: VersionInfo,
        temply_env: TemplyEnv,
        git_env: GitEnv | None = None,
    ):
        """Initialize"""
        self.version_info = version_info
        self.temply_env = temply_env
        self.partial_parser: PartialParser = get_partial_parser(self.temply_env)
        self.template_parser: TemplateParser = get_template_parser(self.temply_env)
        self.git_env: GitEnv | None = git_env

    async def create(self, user: User, partial_create: PartialCreate) -> Partial:
        """Create Partial"""
        partial = await self.partial_parser.create(
            user,
            partial_create.name,
            partial_create.content,
            partial_create.description,
            partial_create.dependencies,
        )
        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
                user,
                f"Create partial {partial.name}",
                [f"{self.temply_env.build_partial_path(partial.name)}"],
            )
        return Partial.model_validate(partial)

    async def get(self, partial_name: str) -> Partial:
        """Get Partial"""
        partial = await self.partial_parser.get_partial(partial_name)
        return Partial.model_validate(partial)

    async def list(self) -> List[Partial]:
        """List Partials"""
        partials = await self.partial_parser.get_partials()
        return [Partial.model_validate(partial) for partial in partials]

    async def get_root(self) -> List[Partial]:
        """Get Root"""
        partials = await self.partial_parser.get_partials()
        return [Partial.model_validate(partial) for partial in partials if not partial.dependencies]

    async def get_children(self, partial_name: str) -> List[Partial]:
        """Get Children"""
        # 먼저 파셜이 존재하는지 확인
        partial = await self.partial_parser.get_partial(partial_name)
        return [Partial.model_validate(p) for p in partial.children]

    async def get_parents(self, partial_name: str) -> List[Partial]:
        """Get Parents"""
        partial = await self.partial_parser.get_partial(partial_name)
        return [Partial.model_validate(p) for p in partial.parents]

    async def update(self, user: User, partial_name: str, partial_update: PartialUpdate) -> Partial:
        """Update Partial"""
        partial = await self.partial_parser.update(
            user,
            partial_name,
            partial_update.content,
            partial_update.description,
            partial_update.dependencies,
        )
        # updated_partial_files = []
        # for partial in partial.children:
        #     updated_partial_files.append(
        #         f"{partial.name}/{self.temply_env.build_partial_path(partial.name)}"
        #     )
        # updated_template_files = []
        # for template in partial.templates:
        #     updated_template_files.append(
        #         f"{template.name}/{self.temply_env.build_template_path(template.name)}"
        #     )
        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
                user,
                f"Update partial {partial_name}",
                [f"{self.temply_env.build_partial_path(partial_name)}"],
            )
        return Partial.model_validate(partial)

    async def delete(self, user: User, partial_name: str) -> None:
        """Delete Partial"""
        await self.partial_parser.delete(user, partial_name)
        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
                user,
                f"Delete partial {partial_name}",
                [f"{self.temply_env.build_partial_path(partial_name)}"],
            )
