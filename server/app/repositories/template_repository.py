"""
템플릿 리포지토리
"""

from typing import List

from app.core.temply.parser.template_parser import TemplateParser
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User
from app.models.template_model import Template, TemplateCreate, TemplateUpdate


class TemplateRepository:
    """템플릿 리포지토리"""

    def __init__(self, temply_env: TemplyEnv):
        """초기화"""
        self.temply_env = temply_env
        self.template_parser = TemplateParser(self.temply_env)

    async def create(self, user: User, category_name: str, template: TemplateCreate) -> Template:
        """템플릿 생성"""
        template = await self.template_parser.create(
            user,
            category_name,
            template.name,
            template.content,
            template.description,
            template.layout,
            template.partials,
        )

        return Template.model_validate(template)

    async def get(self, category_name: str, template_name: str) -> Template:
        """템플릿 조회"""
        template = await self.template_parser.get_template(f"{category_name}/{template_name}")
        return Template.model_validate(template)

    async def list(self) -> List[Template]:
        """List Templates"""
        templates = await self.template_parser.get_templates()
        return [Template.model_validate(template) for template in templates]

    async def update(
        self, user: User, category_name: str, template_name: str, template: TemplateUpdate
    ) -> Template:
        """템플릿 수정"""
        updated_template = await self.template_parser.update(
            user,
            category_name,
            template_name,
            template.content,
            template.description,
            template.layout,
            template.partials,
        )
        return Template.model_validate(updated_template)

    async def delete(self, user: User, category_name: str, template_name: str) -> None:
        """템플릿 삭제"""
        await self.template_parser.delete(user, category_name, template_name)

    async def get_categories(self) -> List[str]:
        """Get Categories"""
        return await self.template_parser.get_categories()

    async def get_templates(self, category_name: str) -> List[Template]:
        """Get Templates"""
        return await self.template_parser.get_templates_by_category(category_name)

    async def delete_templates(self, user: User, category_name: str) -> None:
        """Delete Templates"""
        await self.template_parser.delete_templates(user, category_name)
