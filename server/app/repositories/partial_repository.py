"""Partial Repository"""

from typing import List

from app.core.temply.parser.partial_parser import PartialParser
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User
from app.models.partial_model import Partial, PartialCreate, PartialUpdate


class PartialRepository:
    """Partial Repository"""

    def __init__(self, temply_env: TemplyEnv):
        """Initialize"""
        self.temply_env = temply_env
        self.partial_parser = PartialParser(self.temply_env)

    async def create(self, user: User, partial: PartialCreate) -> Partial:
        """Create Partial"""
        partial_meta = await self.partial_parser.create(
            user, partial.name, partial.content, partial.description, partial.dependencies
        )
        return Partial.model_validate(partial_meta)

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

    async def update(self, user: User, partial_name: str, partial: PartialUpdate) -> Partial:
        """Update Partial"""
        partial = await self.partial_parser.update(
            user, partial_name, partial.content, partial.description, partial.dependencies
        )
        return Partial.model_validate(partial)

    async def delete(self, user: User, partial_name: str) -> None:
        """Delete Partial"""
        await self.partial_parser.delete(user, partial_name)
