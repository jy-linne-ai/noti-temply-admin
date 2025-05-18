from app.core.temply.parser.meta_model import BaseMetaData
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
        meta = BaseMetaData(
            description=partial.description,
            created_at=BaseMetaData.get_current_datetime(),
            created_by=user.name,
            updated_at=BaseMetaData.get_current_datetime(),
            updated_by=user.name,
        )
        partial_meta = await self.partial_parser.create(
            partial.name, partial.content, meta, partial.dependencies
        )
        return Partial.model_validate(partial_meta)

    async def get(self, name: str) -> Partial:
        """Get Partial"""
        partial = await self.partial_parser.get_partial(name)
        return Partial.model_validate(partial)

    async def update(self, user: User, name: str, partial: PartialUpdate) -> Partial:
        """Update Partial"""
        meta = BaseMetaData(
            description=partial.description,
            updated_at=BaseMetaData.get_current_datetime(),
            updated_by=user.name,
        )
        partial = await self.partial_parser.update(name, partial.content, meta)
        return Partial.model_validate(partial)

    async def delete(self, name: str) -> None:
        """Delete Partial"""
        await self.partial_parser.delete(name)
