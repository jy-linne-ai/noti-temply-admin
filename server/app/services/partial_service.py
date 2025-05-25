"""Partial Service"""

from typing import List

from app.models.common_model import User
from app.models.partial_model import Partial, PartialCreate, PartialUpdate
from app.repositories.partial_repository import PartialRepository


class PartialService:
    """Partial Service"""

    def __init__(self, repository: PartialRepository):
        """Initialize"""
        self.repository = repository

    async def get_root(self) -> List[Partial]:
        """Get Root"""
        return await self.repository.get_root()

    async def get_children(self, partial_name: str) -> List[Partial]:
        """Get Children"""
        return await self.repository.get_children(partial_name)

    # async def get_parents(self, partial_name: str) -> List[Partial]:
    #     """Get Parents"""
    #     return await self.repository.get_parents(partial_name)

    async def create(self, user: User, partial_create: PartialCreate) -> Partial:
        """Create Partial"""
        return await self.repository.create(user, partial_create)

    async def get(self, partial_name: str) -> Partial:
        """Get Partial"""
        return await self.repository.get(partial_name)

    async def list(self) -> List[Partial]:
        """List Partials"""
        return await self.repository.list()

    async def update(self, user: User, partial_name: str, partial_update: PartialUpdate) -> Partial:
        """Update Partial"""
        return await self.repository.update(user, partial_name, partial_update)

    async def delete(self, user: User, partial_name: str) -> None:
        """Delete Partial"""
        await self.repository.delete(user, partial_name)
