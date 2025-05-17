"""Template parser module.

This module provides functionality to parse Jinja2 templates.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Set

from jinja2 import nodes

from app.core.temply.metadata.meta_model import TemplateMetaData
from app.core.temply.metadata.meta_parser import parse_meta_from_content
from app.core.temply.temply_env import TemplyEnv


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
        self._init_task = asyncio.create_task(self._initialize())

    async def _initialize(self):
        """초기화 작업을 수행합니다."""
        await self._build_template_tree(await self._parse_template_files())
        self._initialized = True

    async def _ensure_initialized(self):
        """초기화가 완료될 때까지 기다립니다."""
        if not self._initialized:
            await self._init_task

    async def _parse_template(self, category_name: str, template_name: str) -> TemplateMetaData:
        """Parse a template file.

        Args:
            template_file: Path to the template file

        Returns:
            TemplateMetaData: Parsed template metadata
        """
        content, _, _ = self.env.get_source_template(category_name, template_name)
        meta = parse_meta_from_content(content)
        return TemplateMetaData(
            category=category_name,
            name=template_name,
            content=content,
            description=meta.description,
            created_at=meta.created_at,
            created_by=meta.created_by,
            updated_at=meta.updated_at,
            updated_by=meta.updated_by,
        )

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
        for file_info in templates:
            ast = self.env.parse(file_info.content)
            file_info.layout = await self._extract_layout(ast)
            file_info.partials = await self._extract_partials(ast)
            self.nodes[file_info.name] = file_info

    async def _extract_layout(self, ast: nodes.Template) -> Optional[str]:
        """Extract layout from template content using AST.

        Args:
            content: Template content

        Returns:
            Optional[str]: Layout name if found, None otherwise
        """
        for node in ast.body:
            if isinstance(node, nodes.Extends):
                template_name = node.template.as_const()
                if template_name.startswith(f"{self.env.layouts_dir_name}/"):
                    return template_name

        return None

    async def _extract_partials(self, ast: nodes.Template) -> List[str]:
        """Extract partials from template content using AST.

        Args:
            content: Template content

        Returns:
            List[str]: List of partial names
        """
        partials = []
        for node in ast.body:
            # import 구문
            if isinstance(node, nodes.Import):
                template_name = node.template.as_const()
                if template_name.startswith(f"{self.env.partials_dir_name}/"):
                    partials.append(template_name)

            # include 구문
            elif isinstance(node, nodes.Include):
                template_name = node.template.as_const()
                if template_name.startswith(f"{self.env.partials_dir_name}/"):
                    partials.append(template_name)

            # from ... import 구문
            elif isinstance(node, nodes.FromImport):
                template_name = node.template.as_const()
                if template_name.startswith(f"{self.env.partials_dir_name}/"):
                    partials.append(template_name)

            # macro 구문은 현재 노드에서 직접 처리하지 않음
            # (매크로는 다른 템플릿에서 import할 때 처리)
        return partials

    async def get_templates(self) -> List[TemplateMetaData]:
        """List all templates.

        Returns:
            List of all templates
        """
        await self._ensure_initialized()
        return list(self.nodes.values())

    async def get_template(self, name: str) -> Optional[TemplateMetaData]:
        """Get a template by name.

        Args:
            name: Name of the template
        """
        await self._ensure_initialized()
        return self.nodes.get(name)

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
            for root in await self.get_templates():
                await self.print_template_tree(root, level, visited)
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
            print(f"{layout_indent}레이아웃: {node.layout}")

        # 파셜 정보 출력
        if node.partials:
            partials_indent = "  " * (level + 1)
            print(f"{partials_indent}파셜: {', '.join(sorted(node.partials))}")

        print()  # 빈 줄로 구분
