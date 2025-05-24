"""
템플릿 리포지토리
"""

from typing import List

from app.core.temply.parser.template_parser import TemplateParser
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User
from app.models.template_model import (
    TemplateComponent,
    TemplateComponentCreate,
    TemplateComponentUpdate,
)


class TemplateRepository:
    """템플릿 리포지토리"""

    def __init__(self, temply_env: TemplyEnv):
        """초기화"""
        self.temply_env = temply_env
        self.template_parser = TemplateParser(self.temply_env)

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

    async def get_component(self, template: str, component: str) -> TemplateComponent:
        """템플릿 조회"""
        component = await self.template_parser.get_component(template, component)
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
        template: str,
        component: str,
        component_update: TemplateComponentUpdate,
    ) -> TemplateComponent:
        """템플릿 수정"""
        updated_component = await self.template_parser.update_component(
            user,
            template,
            component,
            component_update.content,
            component_update.description,
            component_update.layout,
            component_update.partials,
        )
        return TemplateComponent.model_validate(updated_component)

    async def delete_component(self, user: User, template: str, component: str) -> None:
        """템플릿 삭제"""
        await self.template_parser.delete_component(user, template, component)

    async def get_template_names(self) -> List[str]:
        """Get Template Names"""
        return await self.template_parser.get_template_names()

    async def get_component_names_by_template(self, template: str) -> List[str]:
        """Get Component Names by Template"""
        return await self.template_parser.get_component_names_by_template(template)

    async def get_components_by_template(self, template: str) -> List[TemplateComponent]:
        """Get Components by Template"""
        return await self.template_parser.get_components_by_template(template)

    async def delete_components_by_template(self, user: User, template: str) -> None:
        """Delete Components by Template"""
        await self.template_parser.delete_components_by_template(user, template)
