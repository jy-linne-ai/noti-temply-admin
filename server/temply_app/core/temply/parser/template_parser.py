"""Template parser module.

This module provides functionality to parse Jinja2 templates.
"""

import asyncio
import json
import os
import shutil
from typing import Any, List, Optional, Set

from jinja2 import nodes

from temply_app.core.exceptions import (
    LayoutNotFoundError,
    PartialNotFoundError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
)
from temply_app.core.temply.parser.meta_model import BaseMetaData, TemplateComponentMetaData
from temply_app.core.temply.temply_env import TemplyEnv
from temply_app.core.utils import parser_meta_util
from temply_app.models.common_model import User


class TemplateParser:
    """Parser for Jinja2 templates."""

    def __init__(self, temply_env: TemplyEnv):
        """Initialize the parser.

        Args:
            templates_dir: Directory containing template files
        """
        self.env = temply_env
        self.nodes: dict[str, TemplateComponentMetaData] = {}
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
            await self._build_component_tree(await self._parse_component_files())
            self._initialized = True

    async def _ensure_initialized(self):
        """초기화가 완료될 때까지 기다립니다."""
        if not self._initialized:
            if self._init_task is not None:
                await self._init_task
            else:
                await self._initialize()

    async def _parse_component(
        self, template_name: str, component_name: str
    ) -> TemplateComponentMetaData:
        """Parse a component file.

        Args:
            component_file: Path to the component file

        Returns:
            TemplateComponentMetaData: Parsed component metadata
        """
        try:
            content, _, _ = self.env.load_component_source(template_name, component_name)
            meta, block = parser_meta_util.parse(content)
            layout, block = await self._extract_layout(block)
            partials, block = await self._extract_partials(block)
            return TemplateComponentMetaData(
                template=template_name,
                component=component_name,
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
            raise TemplateNotFoundError(
                f"Template {template_name}/{component_name} not found: {e}"
            ) from e

    async def _parse_component_files(self) -> List[TemplateComponentMetaData]:
        """Parse component files and extract metadata.

        Returns:
            List[TemplateComponentMetaData]: List of template metadata
        """
        components = []
        for template in self.env.get_template_names():
            for component in self.env.get_component_names(template):
                components.append(await self._parse_component(template, component))
        return components

    async def _build_component_tree(self, components: List[TemplateComponentMetaData]) -> None:
        """Build the component tree.

        Returns:
            Dictionary mapping template names to their nodes
        """
        # First pass: Create all nodes
        for component in components:
            self.nodes[component.template + "/" + component.component] = component

    async def _extract_layout(self, content: str) -> tuple[str, str]:
        """Extract layout from component content using AST.

        Args:
            content: Component content

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
        """Extract partials from component content using AST.

        Args:
            content: Component content

        Returns:
            List[str]: List of partial names
        """
        partials = []
        last_import_line = 0
        ast = self.env.parse(content)
        for node in ast.body:
            # import 구문
            if isinstance(node, (nodes.Import, nodes.FromImport)):
                partial_name = node.template.as_const()
                if partial_name.startswith(f"{self.env.partials_dir_name}/"):
                    partials.append(partial_name.split("/")[-1])
                    last_import_line = node.lineno

        return partials, "\n".join(content.splitlines()[last_import_line:])

    async def get_templates(self) -> List[TemplateComponentMetaData]:
        """Get all templates."""
        await self._ensure_initialized()
        return list(self.nodes.values())

    async def get_template_names(self) -> List[str]:
        """Get all templates."""
        await self._ensure_initialized()
        return list(set(template.template for template in self.nodes.values()))

    async def get_components(self) -> List[TemplateComponentMetaData]:
        """List all components.

        Returns:
            List of all components
        """
        await self._ensure_initialized()
        return list(self.nodes.values())

    async def get_components_by_template(
        self, template_name: str
    ) -> List[TemplateComponentMetaData]:
        """Get all components in a template."""
        await self._ensure_initialized()
        return [
            component for component in self.nodes.values() if component.template == template_name
        ]

    async def sync_schema(self, template_name: str) -> str | None:
        """Sync schema by template."""
        await self._ensure_initialized()
        load_schema_source = self.env.load_schema_source(template_name)
        schema = self.env.get_template_schema(template_name)
        if schema == load_schema_source:
            return None
        schema_path = self.env.templates_dir / self.env.build_component_schema_path(template_name)
        with open(schema_path, "w", encoding=self.env.file_encoding) as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        return f"{template_name}/{schema_path.name}"

    async def get_schema_by_template(self, template_name: str) -> dict[str, Any]:
        """Get schema by template."""
        await self._ensure_initialized()
        return self.env.load_schema_source(template_name)

    async def get_variables_by_template(self, template_name: str) -> dict[str, Any]:
        """Get variables by template."""
        await self._ensure_initialized()
        return self.env.get_template_schema_generator(template_name)

    async def get_component_names_by_template(self, template_name: str) -> List[str]:
        """Get all component names in a template."""
        await self._ensure_initialized()
        return [
            component.component
            for component in self.nodes.values()
            if component.template == template_name
        ]

    async def get_component(
        self, template_name: str, component_name: str
    ) -> TemplateComponentMetaData:
        """Get a template component by name.

        Args:
            name: Name of the template
        """
        await self._ensure_initialized()
        component = self.nodes.get(template_name + "/" + component_name)
        if not component:
            raise TemplateNotFoundError(f"Template {template_name}/{component_name} not found")
        return component

    async def print_component_tree(
        self,
        node: Optional[TemplateComponentMetaData] = None,
        level: int = 0,
        visited: Optional[Set[str]] = None,
    ) -> None:
        """Print the component tree with detailed information.

        Args:
            node: Node to start printing from (defaults to root nodes)
            level: Current indentation level
            visited: Set of visited node names to prevent cycles
        """
        await self._ensure_initialized()

        if visited is None:
            visited = set()

        if node is None:
            print("\n=== 컴포넌트 트리 구조 ===")
            for node in self.nodes.values():
                await self.print_component_tree(node, level, visited)
            return

        if node.template + "/" + node.component in visited:
            return

        visited.add(node.template + "/" + node.component)

        # 노드 정보 출력
        indent = "  " * level
        print(f"{indent}└─ {node.template}/{node.component}")

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

    async def create_component(
        self,
        user: User,
        template_name: str,
        component_name: str,
        content: str,
        description: Optional[str] = None,
        layout: Optional[str] = None,
        partials: Optional[List[str]] = None,
    ) -> TemplateComponentMetaData:
        """Create a template.

        Args:
            template_name: Template name
            template_component_name: Template component name
            content: Template content
            layout: Layout name
            partials: List of partial names
            meta: Template metadata

        Returns:
            TemplateComponentMetaData: Created template metadata

        Raises:
            TemplateAlreadyExistsError: If the template already exists
            ValueError: If the template or template component name is invalid
            PartialNotFoundError: If the partial is not found

        """
        await self._ensure_initialized()
        self._initialized = False
        try:
            if not self.env.validate_file_name(template_name):
                raise ValueError(f"Invalid template name: {template_name}")

            if not self.env.validate_component_name(component_name):
                raise ValueError(f"Invalid component name: {component_name}")

            if layout:
                if not self.env.validate_file_name(layout):
                    raise ValueError(f"Invalid layout name: {layout}")
                if not (self.env.layouts_dir / layout).exists():
                    raise LayoutNotFoundError(f"Layout {layout} not found")

            if partials:
                for partial in partials:
                    if not self.env.validate_file_name(partial):
                        raise ValueError(f"Invalid partial name: {partial}")
                    if not (self.env.partials_dir / partial).exists():
                        raise PartialNotFoundError(f"Partial {partial} not found")

            component_path = f"{template_name}/{component_name}"
            if component_path in self.nodes:
                raise TemplateAlreadyExistsError(f"Template {component_path} already exists")
            if (self.env.templates_dir / component_path).exists():
                raise TemplateAlreadyExistsError(f"Template {component_path} already exists")

            meta = BaseMetaData(
                description=description,
                created_at=BaseMetaData.get_current_datetime(),
                created_by=user.name,
                updated_at=BaseMetaData.get_current_datetime(),
                updated_by=user.name,
            )

            await self._write_component(
                template_name, component_name, content, layout or "", partials or [], meta
            )
            self.nodes[component_path] = await self._parse_component(template_name, component_name)
            return self.nodes[component_path]
        finally:
            self._initialized = True

    async def _write_component(
        self,
        template_name: str,
        component_name: str,
        content: str,
        layout: str,
        partials: List[str],
        meta: BaseMetaData,
    ) -> None:
        """Write a template component."""
        # 템플릿 디렉토리 생성
        template_dir = self.env.templates_dir / template_name
        template_dir.mkdir(parents=True, exist_ok=True)

        with open(
            template_dir / f"{component_name}",
            "w",
            encoding=self.env.file_encoding,
        ) as f:
            f.write(self.env.format_meta_block(meta))
            if layout:
                f.write("\n")
                f.write(self.env.format_layout_block(layout))
            if partials:
                for partial in self.env.format_partial_imports(set(partials)):
                    f.write("\n")
                    f.write(partial)
            f.write("\n")
            f.write(content)
            f.write("\n")

    async def update_component(
        self,
        user: User,
        template_name: str,
        component_name: str,
        content: str,
        description: Optional[str] = None,
        layout: Optional[str] = None,
        partials: Optional[List[str]] = None,
    ) -> TemplateComponentMetaData:
        """Update a component.

        Args:
            template: Template name
            component: Component name
            content: Component content
            meta: Component metadata
        """
        await self._ensure_initialized()
        self._initialized = False

        try:
            if not self.env.validate_file_name(template_name):
                raise ValueError(f"Invalid template name: {template_name}")

            if not self.env.validate_component_name(component_name):
                raise ValueError(f"Invalid component name: {component_name}")

            if layout and not self.env.validate_file_name(layout):
                raise ValueError(f"Invalid layout name: {layout}")

            if partials:
                for partial in partials:
                    if not self.env.validate_file_name(partial):
                        raise ValueError(f"Invalid partial name: {partial}")

            component_path = f"{template_name}/{component_name}"

            if component_path not in self.nodes:
                raise TemplateNotFoundError(f"Template {component_path} not found")
            if not (self.env.templates_dir / component_path).exists():
                raise TemplateNotFoundError(f"Template {component_path} not found")

            _component = await self.get_component(template_name, component_name)
            meta = BaseMetaData(
                description=description,
                created_at=_component.created_at,
                created_by=_component.created_by,
                updated_at=BaseMetaData.get_current_datetime(),
                updated_by=user.name,
            )

            await self._write_component(
                template_name, component_name, content, layout or "", partials or [], meta
            )
            self.nodes[component_path] = await self._parse_component(template_name, component_name)
            return self.nodes[component_path]

        finally:
            self._initialized = True

    async def delete_component(self, user: User, template_name: str, component_name: str) -> None:
        """Delete a component.

        Args:
            template_name: Template name
            component_name: Component name
        """
        await self._ensure_initialized()
        self._initialized = False
        try:
            await self._delete_component(user, template_name, component_name)
        finally:
            self._initialized = True

    async def _delete_component(self, user: User, template_name: str, component_name: str) -> None:
        """Delete a component.

        Args:
            template: Template name
            component: Component name
        """
        component_path = f"{template_name}/{component_name}"
        if component_path not in self.nodes:
            raise TemplateNotFoundError(f"Template {component_path} not found")
        if not (self.env.templates_dir / component_path).exists():
            raise TemplateNotFoundError(f"Template {component_path} not found")
        os.remove(self.env.templates_dir / component_path)
        del self.nodes[component_path]

    async def delete_components_by_template(self, user: User, template_name: str) -> None:
        """Delete components by template."""
        await self._ensure_initialized()
        self._initialized = False
        try:
            for component_name in self.env.get_component_names(template_name):
                await self._delete_component(user, template_name, component_name)
            shutil.rmtree(self.env.templates_dir / template_name)
        finally:
            self._initialized = True

    async def render_component(
        self, template_name: str, component_name: str, data: dict[str, Any]
    ) -> str:
        """Render Component"""
        return self.env.render_component(template_name, component_name, data)

    async def get_components_using_layout(
        self, layout_name: str
    ) -> List[TemplateComponentMetaData]:
        """Get components using layout."""
        await self._ensure_initialized()
        return [component for component in self.nodes.values() if component.layout == layout_name]
