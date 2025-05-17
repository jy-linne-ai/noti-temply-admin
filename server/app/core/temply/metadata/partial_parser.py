"""Partial parser module.

This module provides functionality to parse Jinja2 partials and build a dependency tree.
"""

import asyncio
from typing import List, Optional, Set

from jinja2 import nodes

from app.core.temply.metadata.meta_model import PartialMetaData
from app.core.temply.metadata.meta_parser import parse_meta_from_content
from app.core.temply.temply_env import TemplyEnv


class PartialParser:
    """Parser for Jinja2 partials that builds a dependency tree."""

    def __init__(self, temply_env: TemplyEnv):
        """Initialize the parser.

        Args:
            partials_dir: Directory containing partial templates
        """
        self.env = temply_env
        self.nodes: dict[str, PartialMetaData] = {}
        self._initialized = False
        self._init_task = asyncio.create_task(self._initialize())

    async def _initialize(self):
        """초기화 작업을 수행합니다."""
        await self._build_dependency_tree(await self._parse_partial_files())
        self._initialized = True

    async def _ensure_initialized(self):
        """초기화가 완료될 때까지 기다립니다."""
        if not self._initialized:
            await self._init_task

    async def _parse_partial(self, partial_name: str) -> PartialMetaData:
        """Parse a partial template.

        Args:
            partial_file: Path to the partial template

        Returns:
            PartialMetaData: Parsed partial metadata
        """
        content, _, _ = self.env.get_source_partial(partial_name)
        meta = parse_meta_from_content(content)
        return PartialMetaData(
            name=partial_name,
            content=content,
            description=meta.description,
            created_at=meta.created_at,
            created_by=meta.created_by,
            updated_at=meta.updated_at,
            updated_by=meta.updated_by,
        )

    async def _parse_partial_files(self) -> List[PartialMetaData]:
        """Parse partial files and extract metadata.

        Returns:
            List[PartialMetaData]: List of partial metadata
        """
        partials = []
        for partial_name in self.env.get_partial_names():
            partials.append(await self._parse_partial(partial_name))
        return partials

    async def _extract_dependencies(self, content: str) -> Set[str]:
        """Extract dependencies from partial content using AST.

        Args:
            content: Partial content

        Returns:
            Set[str]: Set of dependency names
        """
        dependencies = set()
        ast = self.env.parse(content)
        for node in ast.body:
            if isinstance(node, nodes.Import):
                template_name = node.template.as_const()
                if template_name.startswith(f"{self.env.partials_dir_name}/"):
                    dependencies.add(template_name.split("/")[-1])
            elif isinstance(node, nodes.FromImport):
                template_name = node.template.as_const()
                if template_name.startswith(f"{self.env.partials_dir_name}/"):
                    dependencies.add(template_name.split("/")[-1])
        return dependencies

    async def _build_dependency_tree(self, partials: List[PartialMetaData]) -> None:
        """Build the dependency tree for all partials.

        Returns:
            Dictionary mapping partial names to their nodes
        """
        # First pass: Create all nodes
        for file_info in partials:
            self.nodes[file_info.name] = file_info

        # Second pass: Build parent-child relationships
        for node in self.nodes.values():
            # 의존성 분석
            dependencies = await self._extract_dependencies(node.content)
            for dep_name in dependencies:
                if dep_name in self.nodes:
                    dep_node = self.nodes[dep_name]
                    node.dependencies.add(dep_name)
                    # 의존하는 노드가 부모가 됨
                    node.parents.append(dep_node)
                    # 현재 노드가 의존하는 노드의 자식이 됨
                    dep_node.children.append(node)

    async def get_partials(self) -> List[PartialMetaData]:
        """List all partials.

        Returns:
            List of all partials
        """
        await self._ensure_initialized()
        return list(self.nodes.values())

    async def get_partial(self, name: str) -> Optional[PartialMetaData]:
        """Get a partial by name.

        Args:
            name: Name of the partial
        """
        await self._ensure_initialized()
        return self.nodes.get(name)

    async def print_dependency_tree(
        self,
        node: Optional[PartialMetaData] = None,
        level: int = 0,
        visited: Optional[Set[str]] = None,
    ) -> None:
        """Print the dependency tree with detailed information.

        Args:
            node: Node to start printing from (defaults to root nodes)
            level: Current indentation level
            visited: Set of visited node names to prevent cycles
        """
        await self._ensure_initialized()

        if visited is None:
            visited = set()

        if node is None:
            print("\n=== 파셜 의존성 트리 구조 ===")
            for root in await self.get_root_partials():
                await self.print_dependency_tree(root, level, visited)
            return

        if node.name in visited:
            return

        visited.add(node.name)

        # 노드 정보 출력
        indent = "  " * level
        print(f"{indent}└─ {node.name}")

        # 의존성 정보 출력
        if node.dependencies:
            deps_indent = "  " * (level + 1)
            print(f"{deps_indent}의존성: {', '.join(sorted(node.dependencies))}")

        # 부모-자식 관계 출력
        if node.parents:
            parents_indent = "  " * (level + 1)
            parent_names = [p.name for p in node.parents]
            print(f"{parents_indent}부모: {', '.join(sorted(parent_names))}")

        if node.children:
            children_indent = "  " * (level + 1)
            child_names = [c.name for c in node.children]
            print(f"{children_indent}자식: {', '.join(sorted(child_names))}")

        print()  # 빈 줄로 구분

        # 자식 노드들 재귀적으로 출력
        for child in node.children:
            await self.print_dependency_tree(child, level + 1, visited)

    async def get_root_partials(self) -> List[PartialMetaData]:
        """Get all root nodes (nodes without parents).

        Returns:
            List of root nodes
        """
        await self._ensure_initialized()
        return [node for node in self.nodes.values() if not node.parents]

    async def print_tree(self, node: Optional[PartialMetaData] = None, level: int = 0) -> None:
        """Print the dependency tree.

        Args:
            node: Node to start printing from (defaults to root nodes)
            level: Current indentation level
        """
        await self._ensure_initialized()

        if node is None:
            for root in await self.get_root_partials():
                await self.print_tree(root, level)
            return
        print("  " * level + f"└─ {node.name}")
        for child in node.children:
            await self.print_tree(child, level + 1)
