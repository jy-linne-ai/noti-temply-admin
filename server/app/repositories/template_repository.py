"""
템플릿 리포지토리
"""

from app.core.temply.parser.meta_model import BaseMetaData
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

    async def create(self, user: User, template: TemplateCreate) -> Template:
        """템플릿 생성"""
        meta = BaseMetaData(
            description=template.description,
            created_at=BaseMetaData.get_current_datetime(),
            created_by=user.name,
            updated_at=BaseMetaData.get_current_datetime(),
            updated_by=user.name,
        )
        template = await self.template_parser.create(
            template.category,
            template.name,
            template.content,
            template.layout,
            template.partials,
            meta,
        )
        return Template.model_validate(template)

    async def get(self, category: str, name: str) -> Template:
        """템플릿 조회"""
        template = await self.template_parser.get_template(f"{category}/{name}")
        return Template.model_validate(template)

    async def update(
        self, user: User, category: str, name: str, template: TemplateUpdate
    ) -> Template:
        """템플릿 수정"""
        existing_template = await self.get(category, name)
        meta = BaseMetaData(
            description=template.description,
            updated_at=BaseMetaData.get_current_datetime(),
            updated_by=user.name,
            created_at=existing_template.created_at,
            created_by=existing_template.created_by,
        )
        updated_template = await self.template_parser.update(
            category,
            name,
            template.content,
            template.layout,
            template.partials or [],
            meta,
        )
        return Template.model_validate(updated_template)

    async def delete(self, category: str, name: str) -> None:
        """템플릿 삭제"""
        await self.template_parser.delete(category, name)
