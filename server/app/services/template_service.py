"""Template Service"""

from typing import List

from app.models.common_model import User
from app.models.template_model import Template, TemplateCreate, TemplateUpdate
from app.repositories.template_repository import TemplateRepository


class TemplateService:
    """Template Service"""

    def __init__(self, repository: TemplateRepository):
        """Initialize"""
        self.repository = repository

    async def create(self, user: User, template: TemplateCreate) -> Template:
        """Create Template"""
        return await self.repository.create(user, template)

    async def get(self, category: str, name: str) -> Template:
        """Get Template"""
        return await self.repository.get(category, name)

    async def list(self) -> List[Template]:
        """List Templates"""
        return await self.repository.list()

    async def update(
        self, user: User, category: str, name: str, template: TemplateUpdate
    ) -> Template:
        """Update Template"""
        return await self.repository.update(user, category, name, template)

    async def delete(self, user: User, category: str, name: str) -> None:
        """Delete Template"""
        return await self.repository.delete(user, category, name)
