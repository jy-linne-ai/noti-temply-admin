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

    async def create(self, user: User, category_name: str, template: TemplateCreate) -> Template:
        """Create Template"""
        return await self.repository.create(user, category_name, template)

    async def get(self, category_name: str, template_name: str) -> Template:
        """Get Template"""
        return await self.repository.get(category_name, template_name)

    async def list(self) -> List[Template]:
        """List Templates"""
        return await self.repository.list()

    async def update(
        self, user: User, category_name: str, template_name: str, template: TemplateUpdate
    ) -> Template:
        """Update Template"""
        return await self.repository.update(user, category_name, template_name, template)

    async def delete(self, user: User, category_name: str, template_name: str) -> None:
        """Delete Template"""
        return await self.repository.delete(user, category_name, template_name)

    async def get_categories(self) -> List[str]:
        """Get Categories"""
        return await self.repository.get_categories()

    async def get_templates(self, category_name: str) -> List[Template]:
        """Get Templates"""
        return await self.repository.get_templates(category_name)

    async def delete_templates(self, user: User, category_name: str) -> None:
        """Delete Templates by Category"""
        return await self.repository.delete_templates(user, category_name)
