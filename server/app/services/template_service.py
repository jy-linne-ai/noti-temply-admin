"""Template Service"""

from typing import List, Optional

from app.models.common_model import User
from app.models.template_model import (
    TemplateComponent,
    TemplateComponentCreate,
    TemplateComponentUpdate,
)
from app.repositories.template_repository import TemplateRepository


class TemplateService:
    """Template Service"""

    def __init__(self, template_repository: TemplateRepository):
        """Initialize"""
        self.template_repository = template_repository

    async def create_component(
        self, user: User, template: str, component_create: TemplateComponentCreate
    ) -> TemplateComponent:
        """Create Template"""
        return await self.template_repository.create_component(user, template, component_create)

    async def get_component(self, template: str, component: str) -> TemplateComponent:
        """Get Template"""
        return await self.template_repository.get_component(template, component)

    async def get_components_by_layout(self, layout_name: str) -> List[TemplateComponent]:
        """List Templates by Layout"""
        return await self.template_repository.get_components_by_layout(layout_name)

    async def get_components(self) -> List[TemplateComponent]:
        """List Components"""
        return await self.template_repository.get_components()

    async def update_component(
        self,
        user: User,
        template: str,
        component: str,
        component_update: TemplateComponentUpdate,
    ) -> TemplateComponent:
        """Update Template"""
        return await self.template_repository.update_component(
            user, template, component, component_update
        )

    async def delete_component(self, user: User, template: str, component: str) -> None:
        """Delete Component"""
        return await self.template_repository.delete_component(user, template, component)

    async def get_template_names(
        self, version: str, layout: Optional[str] = None, partial: Optional[str] = None
    ) -> List[str]:
        """템플릿 이름 목록을 조회합니다.

        Args:
            version: 버전
            layout: 레이아웃 이름 (선택)
            partial: 파셜 이름 (선택)
        """
        return await self.template_repository.get_template_names(version, layout, partial)

    async def get_components_by_template(self, template: str) -> List[TemplateComponent]:
        """Get Components by Template"""
        return await self.template_repository.get_components_by_template(template)

    async def get_component_names_by_template(self, template: str) -> List[str]:
        """Get Component Names by Template"""
        return await self.template_repository.get_component_names_by_template(template)

    async def delete_components_by_template(self, user: User, template: str) -> None:
        """Delete Components by Template"""
        return await self.template_repository.delete_components_by_template(user, template)
