"""
템플릿 리포지토리
"""

from typing import Any, List

from temply_app.core.git_env import GitEnv
from temply_app.core.temply.parser.template_parser import TemplateParser
from temply_app.core.temply.temply_env import TemplyEnv
from temply_app.core.utils.cache_util import get_template_parser
from temply_app.core.utils.git_util import GitUtil
from temply_app.models.common_model import User, VersionInfo
from temply_app.models.template_model import (
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
        git_env: GitEnv | None = None,
    ):
        """초기화"""
        self.version_info = version_info
        self.temply_env = temply_env
        self.template_parser: TemplateParser = get_template_parser(self.temply_env)
        self.git_env: GitEnv | None = git_env

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

        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
                user,
                f"Create template component : {component.template}/{component.component}",
                [
                    f"{self.temply_env.build_component_path(component.template, component.component)}"
                ],
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
        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
                user,
                f"Update template component : {template_name}/{component_name}",
                [f"{self.temply_env.build_component_path(template_name, component_name)}"],
            )
        return TemplateComponent.model_validate(updated_component)

    async def delete_component(self, user: User, template_name: str, component_name: str) -> None:
        """템플릿 삭제"""
        await self.template_parser.delete_component(user, template_name, component_name)
        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
                user,
                f"Delete template component : {template_name}/{component_name}",
                [f"{self.temply_env.build_component_path(template_name, component_name)}"],
            )

    async def get_template_names(self) -> List[str]:
        """Get Template Names"""
        return await self.template_parser.get_template_names()

    async def get_template_component_counts(self) -> dict[str, int]:
        """Get Template Names with Component Counts"""
        result: dict[str, int] = {}
        template_names = await self.template_parser.get_template_names()
        for template_name in template_names:
            components = await self.template_parser.get_components_by_template(template_name)
            result[template_name] = len(components)
        return dict(sorted(result.items(), key=lambda x: x[0], reverse=False))

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

    async def get_schema_by_template(self, template_name: str) -> dict[str, Any]:
        """Get Schema by Template"""
        return await self.template_parser.get_schema_by_template(template_name)

    async def get_variables_by_template(self, template_name: str) -> dict[str, Any]:
        """Get Variables by Template"""
        return await self.template_parser.get_variables_by_template(template_name)

    async def delete_components_by_template(self, user: User, template_name: str) -> None:
        """Delete Components by Template"""
        components = await self.template_parser.get_components_by_template(template_name)
        await self.template_parser.delete_components_by_template(user, template_name)
        if self.git_env:
            GitUtil.commit_version(
                self.git_env,
                user,
                f"Delete template : {template_name}",
                [
                    f"{self.temply_env.build_component_path(template_name, component.component)}"
                    for component in components
                ],
            )

    async def render_component(
        self, template_name: str, component_name: str, data: dict[str, Any]
    ) -> str:
        """Render Component"""
        return await self.template_parser.render_component(template_name, component_name, data)
