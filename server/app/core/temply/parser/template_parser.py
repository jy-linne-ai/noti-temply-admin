"""Template parser module.

This module provides functionality to parse Jinja2 templates.
"""

import asyncio
import os
from typing import List, Optional, Set

from jinja2 import nodes

from app.core.exceptions import (
    LayoutNotFoundError,
    PartialNotFoundError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
)
from app.core.temply.parser.meta_model import BaseMetaData, TemplateMetaData
from app.core.temply.parser.meta_parser import MetaParser
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User


class TemplateParser:
    """Parser for Jinja2 templates."""

    def __init__(self, temply_env: TemplyEnv):
        """Initialize the parser.

        Args:
            templates_dir: Directory containing template files
        """
        self.env = temply_env
        self.nodes: dict[str, TemplateMetaData] = {}
        self._initialized = False
        self._init_task = None

        # 초기화 시작
        try:
            # FastAPI 환경에서 실행 중인 경우
            loop = asyncio.get_running_loop()
            self._init_task = asyncio.create_task(self._initialize())
        except RuntimeError:
            # 테스트 환경에서 실행 중인 경우
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._initialize())
            finally:
                loop.close()

    async def _initialize(self):
        """초기화 작업을 수행합니다."""
        if not self._initialized:
            await self._build_template_tree(await self._parse_template_files())
            self._initialized = True

    async def _ensure_initialized(self):
        """초기화가 완료될 때까지 기다립니다."""
        if not self._initialized:
            if self._init_task is not None:
                await self._init_task
            else:
                await self._initialize()

    async def _parse_template(self, category_name: str, template_name: str) -> TemplateMetaData:
        """Parse a template file.

        Args:
            template_file: Path to the template file

        Returns:
            TemplateMetaData: Parsed template metadata
        """
        try:
            content, _, _ = self.env.get_source_template(category_name, template_name)
            meta, block = MetaParser.parse(content)
            layout, block = await self._extract_layout(block)
            partials, block = await self._extract_partials(block)
            block = await self._remove_block_wrapper(block)
            return TemplateMetaData(
                category=category_name,
                name=template_name,
                content=block.strip(),
                layout=layout,
                partials=partials,
                description=meta.description,
                created_at=meta.created_at,
                created_by=meta.created_by,
                updated_at=meta.updated_at,
                updated_by=meta.updated_by,
            )
        except FileNotFoundError as e:
            raise TemplateNotFoundError(f"Template {template_name} not found: {e}") from e

    async def _parse_template_files(self) -> List[TemplateMetaData]:
        """Parse template files and extract metadata.

        Returns:
            List[TemplateMetaData]: List of template metadata
        """
        templates = []
        for category_name in self.env.get_category_names():
            for template_name in self.env.get_template_names(category_name):
                templates.append(await self._parse_template(category_name, template_name))
        return templates

    async def _build_template_tree(self, templates: List[TemplateMetaData]) -> None:
        """Build the template tree.

        Returns:
            Dictionary mapping template names to their nodes
        """
        # First pass: Create all nodes
        for template in templates:
            self.nodes[template.category + "/" + template.name] = template

    async def _extract_layout(self, content: str) -> tuple[str, str]:
        """Extract layout from template content using AST.

        Args:
            content: Template content

        Returns:
            Optional[str]: Layout name if found, None otherwise
        """
        ast = self.env.parse(content)
        for node in ast.body:
            if isinstance(node, nodes.Extends):
                layout_name = node.template.as_const()
                if layout_name.startswith(f"{self.env.layouts_dir_name}/"):
                    return layout_name.split("/")[-1], "\n".join(
                        content.splitlines()[node.lineno :]
                    )

        return "", content

    async def _extract_partials(self, content: str) -> tuple[List[str], str]:
        """Extract partials from template content using AST.

        Args:
            content: Template content

        Returns:
            List[str]: List of partial names
        """
        partials = []
        last_import_line = 0
        ast = self.env.parse(content)
        for node in ast.body:
            # import 구문
            if isinstance(node, (nodes.Import, nodes.FromImport)):
                template_name = node.template.as_const()
                if template_name.startswith(f"{self.env.partials_dir_name}/"):
                    partials.append(template_name.split("/")[-1])
                    last_import_line = node.lineno
            elif isinstance(node, nodes.Block):
                break

        return partials, "\n".join(content.splitlines()[last_import_line:])

    async def _remove_block_wrapper(self, content: str) -> str:
        """Remove block wrapper from template content."""
        lines = content.splitlines()
        return "\n".join(lines[1:-1]) if len(lines) > 2 else ""

    async def get_categories(self) -> List[str]:
        """Get all categories."""
        await self._ensure_initialized()
        return list(set(template.category for template in self.nodes.values()))

    async def get_templates(self) -> List[TemplateMetaData]:
        """List all templates.

        Returns:
            List of all templates
        """
        await self._ensure_initialized()
        return list(self.nodes.values())

    async def get_templates_by_category(self, category: str) -> List[TemplateMetaData]:
        """Get all templates in a category."""
        await self._ensure_initialized()
        return [template for template in self.nodes.values() if template.category == category]

    async def get_template(self, template_path: str) -> TemplateMetaData:
        """Get a template by name.

        Args:
            name: Name of the template
        """
        await self._ensure_initialized()
        template = self.nodes.get(template_path)
        if template is None:
            raise TemplateNotFoundError(f"Template {template_path} not found")
        return template

    async def print_template_tree(
        self,
        node: Optional[TemplateMetaData] = None,
        level: int = 0,
        visited: Optional[Set[str]] = None,
    ) -> None:
        """Print the template tree with detailed information.

        Args:
            node: Node to start printing from (defaults to root nodes)
            level: Current indentation level
            visited: Set of visited node names to prevent cycles
        """
        await self._ensure_initialized()

        if visited is None:
            visited = set()

        if node is None:
            print("\n=== 템플릿 트리 구조 ===")
            for node in self.nodes.values():
                await self.print_template_tree(node, level, visited)
            return

        if node.name in visited:
            return

        visited.add(node.name)

        # 노드 정보 출력
        indent = "  " * level
        print(f"{indent}└─ {node.name}")

        # 레이아웃 정보 출력
        if node.layout:
            layout_indent = "  " * (level + 1)
            print(f"{layout_indent}레이아웃: {self.env.layouts_dir_name}/{node.layout}")

        # 파셜 정보 출력
        if node.partials:
            partials_indent = "  " * (level + 1)
            print(
                f"{partials_indent}파셜: {', '.join(sorted(self.env.partials_dir_name + '/' + partial for partial in node.partials))}"
            )

        print()  # 빈 줄로 구분

    async def create(
        self,
        user: User,
        category_name: str,
        template_name: str,
        content: str,
        description: Optional[str] = None,
        layout: Optional[str] = None,
        partials: Optional[List[str]] = None,
    ) -> TemplateMetaData:
        """Create a template.

        Args:
            category_name: Category name
            template_name: Template name
            content: Template content
            layout: Layout name
            partials: List of partial names
            meta: Template metadata

        Returns:
            TemplateMetaData: Created template metadata

        Raises:
            TemplateAlreadyExistsError: If the template already exists
            ValueError: If the category or template name is invalid
            PartialNotFoundError: If the partial is not found

        """
        await self._ensure_initialized()
        self._initialized = False
        try:

            if not self.env.check_file_name(category_name):
                raise ValueError(f"Invalid category name: {category_name}")

            if not self.env.check_template_name(template_name):
                raise ValueError(f"Invalid template name: {template_name}")

            if layout:
                if not self.env.check_file_name(layout):
                    raise ValueError(f"Invalid layout name: {layout}")
                if not (self.env.layouts_dir / layout).exists():
                    raise LayoutNotFoundError(f"Layout {layout} not found")

            if partials:
                for partial in partials:
                    if not self.env.check_file_name(partial):
                        raise ValueError(f"Invalid partial name: {partial}")
                    if not (self.env.partials_dir / partial).exists():
                        raise PartialNotFoundError(f"Partial {partial} not found")

            template_path = f"{category_name}/{template_name}"
            if template_path in self.nodes:
                raise TemplateAlreadyExistsError(f"Template {template_path} already exists")
            if (self.env.templates_dir / template_path).exists():
                raise TemplateAlreadyExistsError(f"Template {template_path} already exists")

            meta = BaseMetaData(
                description=description,
                created_at=BaseMetaData.get_current_datetime(),
                created_by=user.name,
                updated_at=BaseMetaData.get_current_datetime(),
                updated_by=user.name,
            )

            await self._write_template(
                category_name, template_name, content, layout, partials, meta
            )
            self.nodes[template_path] = await self._parse_template(category_name, template_name)
            return self.nodes[template_path]
        finally:
            self._initialized = True

    async def _write_template(
        self,
        category_name: str,
        template_name: str,
        content: str,
        layout: str,
        partials: List[str],
        meta: BaseMetaData,
    ) -> None:
        """Write a template."""
        # 카테고리 디렉토리 생성
        category_dir = self.env.templates_dir / category_name
        category_dir.mkdir(parents=True, exist_ok=True)

        with open(
            category_dir / f"{template_name}",
            "w",
            encoding=self.env.file_encoding,
        ) as f:
            f.write(self.env.make_meta_jinja_format(meta))
            if layout:
                f.write("\n")
                f.write(self.env.make_layout_jinja_format(layout))
            if partials:
                for partial in self.env.make_partials_jinja_format(partials):
                    f.write("\n")
                    f.write(partial)
            f.write("\n")
            f.write(self.env.make_template_body_jinja_format(content))
            f.write("\n")

    async def _write_template_dependencies(
        self, category_name: str, template_name: str, dependencies: List[str]
    ) -> None:
        """Write template dependencies."""
        with open(
            self.env.templates_dir / category_name / f"{template_name}.jinja",
            "w",
            encoding=self.env.file_encoding,
        ) as f:
            for dependency in dependencies:
                f.write(
                    f"{{%- from '{dependency}' import render as {dependency} with context -%}}\n"
                )

    async def _write_template_partials(
        self, category_name: str, template_name: str, partials: List[str]
    ) -> None:
        """Write template partials."""
        with open(
            self.env.templates_dir / category_name / f"{template_name}.jinja",
            "w",
            encoding=self.env.file_encoding,
        ) as f:
            for partial in partials:
                f.write(f"{{%- include '{partial}' -%}}\n")

    async def _write_template_layout(
        self, category_name: str, template_name: str, layout: str
    ) -> None:
        """Write template layout."""
        with open(
            self.env.templates_dir / category_name / f"{template_name}.jinja",
            "w",
            encoding=self.env.file_encoding,
        ) as f:
            f.write(f"{{%- extends '{layout}' -%}}\n")

    async def update(
        self,
        user: User,
        category_name: str,
        template_name: str,
        content: str,
        description: Optional[str] = None,
        layout: Optional[str] = None,
        partials: Optional[List[str]] = None,
    ) -> TemplateMetaData:
        """Update a template.

        Args:
            category_name: Category name
            template_name: Template name
            content: Template content
            meta: Template metadata
        """
        await self._ensure_initialized()
        self._initialized = False

        try:
            if not self.env.check_file_name(category_name):
                raise ValueError(f"Invalid category name: {category_name}")

            if not self.env.check_file_name(template_name):
                raise ValueError(f"Invalid template name: {template_name}")

            if layout and not self.env.check_file_name(layout):
                raise ValueError(f"Invalid layout name: {layout}")

            if partials:
                for partial in partials:
                    if not self.env.check_file_name(partial):
                        raise ValueError(f"Invalid partial name: {partial}")

            template_path = f"{category_name}/{template_name}"

            if template_path not in self.nodes:
                raise TemplateNotFoundError(f"Template {template_path} not found")
            if not (self.env.templates_dir / template_path).exists():
                raise TemplateNotFoundError(f"Template {template_path} not found")

            template = await self.get_template(template_path)
            meta = BaseMetaData(
                description=description,
                created_at=template.created_at,
                created_by=template.created_by,
                updated_at=BaseMetaData.get_current_datetime(),
                updated_by=user.name,
            )

            await self._write_template(
                category_name, template_name, content, layout, partials, meta
            )
            self.nodes[template_path] = await self._parse_template(category_name, template_name)
            return self.nodes[template_path]

        finally:
            self._initialized = True

    async def delete(self, user: User, category_name: str, template_name: str) -> None:
        """Delete a template.

        Args:
            category_name: Category name
            template_name: Template name
        """
        await self._ensure_initialized()
        self._initialized = False
        try:
            await self._delete(user, category_name, template_name)
        finally:
            self._initialized = True

    async def _delete(self, user: User, category_name: str, template_name: str) -> None:
        """Delete a template.

        Args:
            category_name: Category name
            template_name: Template name
        """
        template_path = f"{category_name}/{template_name}"
        if template_path not in self.nodes:
            raise TemplateNotFoundError(f"Template {template_path} not found")
        if not (self.env.templates_dir / template_path).exists():
            raise TemplateNotFoundError(f"Template {template_path} not found")
        os.remove(self.env.templates_dir / template_path)
        del self.nodes[template_path]

    async def delete_templates(self, user: User, category_name: str) -> None:
        """Delete Templates"""
        await self._ensure_initialized()
        self._initialized = False
        try:
            for template_name in self.env.get_template_names(category_name):
                await self._delete(user, category_name, template_name)
            os.rmdir(self.env.templates_dir / category_name)
        finally:
            self._initialized = True
