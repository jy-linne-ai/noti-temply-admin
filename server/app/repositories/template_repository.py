"""
템플릿 리포지토리
"""

from typing import List, Optional

from app.core.git_env import GitEnv
from app.core.temply.parser.template_parser import TemplateParser
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User, VersionInfo
from app.models.template_model import (
    TemplateComponent,
    TemplateComponentCreate,
    TemplateComponentUpdate,
)


class TemplateRepository:
    """템플릿 리포지토리"""

    def __init__(
        self,
        version_info: VersionInfo,
        temply_env: TemplyEnv,
        git_env: Optional[GitEnv] = None,
    ):
        """초기화"""
        self.version_info = version_info
        self.temply_env = temply_env
        self.template_parser = TemplateParser(self.temply_env)
        self.git_env = git_env

    async def create_component(
        self, user: User, template: str, component_create: TemplateComponentCreate
    ) -> TemplateComponent:
        """템플릿 생성"""
        component = await self.template_parser.create_component(
            user,
            template,
            component_create.component,
            component_create.content,
            component_create.description,
            component_create.layout,
            component_create.partials,
        )

        return TemplateComponent.model_validate(component)

    async def get_component(self, template_name: str, component_name: str) -> TemplateComponent:
        """템플릿 조회"""
        component = await self.template_parser.get_component(template_name, component_name)
        return TemplateComponent.model_validate(component)

    async def get_components(self) -> List[TemplateComponent]:
        """List Components"""
        components = await self.template_parser.get_components()
        return [TemplateComponent.model_validate(component) for component in components]

    async def get_components_by_layout(self, layout_name: str) -> List[TemplateComponent]:
        """List Components by Layout"""
        components = await self.template_parser.get_components()
        return [
            TemplateComponent.model_validate(component)
            for component in components
            if component.layout == layout_name
        ]

    async def update_component(
        self,
        user: User,
        template_name: str,
        component_name: str,
        component_update: TemplateComponentUpdate,
    ) -> TemplateComponent:
        """템플릿 수정"""
        updated_component = await self.template_parser.update_component(
            user,
            template_name,
            component_name,
            component_update.content,
            component_update.description,
            component_update.layout,
            component_update.partials,
        )
        return TemplateComponent.model_validate(updated_component)

    async def delete_component(self, user: User, template_name: str, component_name: str) -> None:
        """템플릿 삭제"""
        await self.template_parser.delete_component(user, template_name, component_name)

    async def get_template_names(self) -> List[str]:
        """Get Template Names"""
        return await self.template_parser.get_template_names()

    async def get_templates(self) -> List[TemplateComponent]:
        """Get Templates"""
        templates = await self.template_parser.get_templates()
        return [TemplateComponent.model_validate(template) for template in templates]

    async def get_component_names_by_template(self, template_name: str) -> List[str]:
        """Get Component Names by Template"""
        return await self.template_parser.get_component_names_by_template(template_name)

    async def get_components_by_template(self, template_name: str) -> List[TemplateComponent]:
        """Get Components by Template"""
        components = await self.template_parser.get_components_by_template(template_name)
        return [TemplateComponent.model_validate(component) for component in components]

    async def delete_components_by_template(self, user: User, template_name: str) -> None:
        """Delete Components by Template"""
        await self.template_parser.delete_components_by_template(user, template_name)
