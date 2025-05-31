"""Partial parser module.

This module provides functionality to parse Jinja2 partials and build a dependency tree.
"""

import asyncio
import os
from typing import List, Optional, Set

from jinja2 import nodes

from app.core.exceptions import (
    PartialAlreadyExistsError,
    PartialCircularDependencyError,
    PartialNotFoundError,
)
from app.core.temply.parser import meta_util
from app.core.temply.parser.meta_model import BaseMetaData, PartialMetaData
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User


class PartialParser:
    """Parser for Jinja2 partials that builds a dependency tree."""

    def __init__(self, temply_env: TemplyEnv):
        """Initialize the parser.

        Args:
            temply_env: Temply environment
        """
        self.env = temply_env
        self.nodes: dict[str, PartialMetaData] = {}
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
            await self._build_dependency_tree(await self._parse_partial_files())
            self._initialized = True

    async def _ensure_initialized(self):
        """초기화가 완료될 때까지 기다립니다."""
        if not self._initialized:
            if self._init_task is not None:
                await self._init_task
            else:
                await self._initialize()

    async def _check_circular_dependency(self, partial_name: str, dependencies: Set[str]) -> None:
        """순환 의존성을 검사합니다.

        Args:
            partial_name: 검사할 파셜 이름
            dependencies: 의존성 목록

        Raises:
            PartialCircularDependencyError: 순환 의존성이 발견된 경우
        """
        visited = set()

        async def dfs(node: str, current_path: list[str]) -> None:
            if node == partial_name:
                cycle = current_path + [node]
                raise PartialCircularDependencyError(
                    f"Circular dependency detected: {' -> '.join(cycle)}"
                )
            if node in visited:
                return

            visited.add(node)
            current_path.append(node)

            if node in self.nodes:
                for dep in self.nodes[node].dependencies:
                    await dfs(dep, current_path.copy())

            current_path.pop()

        # 현재 추가하려는 의존성에 대해 DFS 실행
        for dep in dependencies:
            await dfs(dep, [partial_name])

    async def _parse_partial(self, partial_name: str) -> PartialMetaData:
        """Parse a partial template.

        Args:
            partial_file: Path to the partial template

        Returns:
            PartialMetaData: Parsed partial metadata
        """
        try:
            content, _, _ = self.env.load_partial_source(partial_name)
            meta, block = meta_util.parse(content)
            dependencies, block = await self._extract_dependencies(block)
            block = await self._remove_macro_wrapper(block)
            return PartialMetaData(
                name=partial_name,
                content=block,
                dependencies=dependencies,
                description=meta.description,
                created_at=meta.created_at,
                created_by=meta.created_by,
                updated_at=meta.updated_at,
                updated_by=meta.updated_by,
            )
        except FileNotFoundError as e:
            raise PartialNotFoundError(f"Partial {partial_name} not found: {e}") from e

    async def _remove_macro_wrapper(self, content: str) -> str:
        """매크로 래퍼를 제거합니다.

        Args:
            content (str): 매크로가 포함된 내용
            env (TemplyEnv): Jinja2 환경 객체

        Returns:
            str: 매크로 래퍼가 제거된 내용
        """
        ast = self.env.parse(content)
        for node in ast.body:
            if isinstance(node, nodes.Macro):
                return "\n".join(content.splitlines()[1:-1])
        return content

    async def _extract_dependencies(self, content: str) -> tuple[Set[str], str]:
        """Extract dependencies from partial content using AST.

        Args:
            content: Partial content

        Returns:
            tuple[Set[str], str]: (의존성 목록, import 구문이 제외된 본문)
        """
        dependencies = set()
        ast = self.env.parse(content)

        # import 구문 찾기
        last_import_line = 0
        for node in ast.body:
            if isinstance(node, (nodes.Import, nodes.FromImport)):
                template_name = node.template.as_const()
                if template_name.startswith(f"{self.env.partials_dir_name}/"):
                    dependencies.add(template_name.split("/")[-1])
                    last_import_line = node.lineno

        return dependencies, "\n".join(content.splitlines()[last_import_line:])

    async def _parse_partial_files(self) -> List[PartialMetaData]:
        """Parse partial files and extract metadata.

        Returns:
            List[PartialMetaData]: List of partial metadata
        """
        partials = []
        for partial_name in self.env.get_partial_names():
            partials.append(await self._parse_partial(partial_name))
        return partials

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
            for dep_name in node.dependencies:
                if dep_name in self.nodes:
                    dep_node = self.nodes[dep_name]
                    # 의존하는 노드가 부모가 됨
                    if dep_node not in node.parents:
                        node.parents.append(dep_node)
                    # 현재 노드가 의존하는 노드의 자식이 됨
                    if node not in dep_node.children:
                        dep_node.children.append(node)

    async def refresh(self) -> None:
        """Refresh the dependency tree."""
        await self._ensure_initialized()
        self._initialized = False
        try:
            self.nodes = {}
            await self._build_dependency_tree(await self._parse_partial_files())
        finally:
            self._initialized = True

    async def get_partials(self) -> List[PartialMetaData]:
        """List all partials.

        Returns:
            List of all partials
        """
        await self._ensure_initialized()
        return list(self.nodes.values())

    async def get_partial(self, name: str) -> PartialMetaData:
        """Get a partial by name.

        Args:
            name: Name of the partial
        """
        await self._ensure_initialized()
        partial = self.nodes.get(name)
        if partial is None:
            raise PartialNotFoundError(f"Partial {name} not found")
        return partial

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

    async def _write_partial(
        self,
        partial_name: str,
        content: str,
        meta: BaseMetaData,
        dependencies: Set[str] | None = None,
    ) -> None:
        """Write a partial.

        Args:
            partial_name: Name of the partial
            content: Content of the partial
            meta: Metadata of the partial
            dependencies: Dependencies of the partial
        """
        dependencies = dependencies or set()

        for dep in dependencies:
            if dep not in self.nodes:
                raise PartialNotFoundError(f"Dependency {dep} not found")

        await self._check_circular_dependency(partial_name, dependencies)

        with open(self.env.partials_dir / partial_name, "w", encoding=self.env.file_encoding) as f:
            f.write(self.env.format_meta_block(meta))
            if dependencies:
                for dep in self.env.format_partial_imports(dependencies):
                    f.write("\n")
                    f.write(dep)
            f.write("\n")
            f.write(self.env.format_partial_content(content))
            f.write("\n")

    async def create(
        self,
        user: User,
        partial_name: str,
        content: str,
        description: Optional[str] = None,
        dependencies: Set[str] | None = None,
    ) -> PartialMetaData:
        """Create a partial.

        Args:
            user: User who creates the partial
            partial_name: Name of the partial
            content: Content of the partial
            description: Description of the partial
            dependencies: Dependencies of the partial
        """
        await self._ensure_initialized()
        self._initialized = False
        try:
            if not self.env.validate_file_name(partial_name):
                raise ValueError(f"Invalid partial name: {partial_name}")

            if partial_name in self.nodes:
                raise PartialAlreadyExistsError(f"Partial {partial_name} already exists")
            if (self.env.partials_dir / partial_name).exists():
                raise PartialAlreadyExistsError(f"Partial {partial_name} already exists")

            meta = BaseMetaData(
                description=description,
                created_at=BaseMetaData.get_current_datetime(),
                created_by=user.name,
                updated_at=BaseMetaData.get_current_datetime(),
                updated_by=user.name,
            )

            await self._write_partial(partial_name, content, meta, dependencies)

            # 새로운 파셜을 파싱하고 의존성 트리 재구축
            new_partial = await self._parse_partial(partial_name)
            self.nodes[partial_name] = new_partial
            await self._build_dependency_tree(list(self.nodes.values()))
            return self.nodes[partial_name]
        finally:
            self._initialized = True

    async def update(
        self,
        user: User,
        partial_name: str,
        content: str,
        description: Optional[str] = None,
        dependencies: Set[str] | None = None,
    ) -> PartialMetaData:
        """Update a partial."""
        await self._ensure_initialized()
        self._initialized = False
        try:
            if partial_name not in self.nodes:
                raise PartialNotFoundError(f"Partial {partial_name} not found")

            if not (self.env.partials_dir / partial_name).exists():
                raise PartialNotFoundError(f"Partial {partial_name} not found")

            partial = await self.get_partial(partial_name)
            meta = BaseMetaData(
                description=description,
                created_at=partial.created_at,
                created_by=partial.created_by,
                updated_at=BaseMetaData.get_current_datetime(),
                updated_by=user.name,
            )

            await self._write_partial(partial_name, content, meta, dependencies)

            self.nodes[partial_name] = await self._parse_partial(partial_name)
            return self.nodes[partial_name]
        finally:
            self._initialized = True

    async def delete(self, user: User, partial_name: str) -> None:
        """Delete a partial."""
        await self._ensure_initialized()
        self._initialized = False
        try:
            if partial_name not in self.nodes:
                raise PartialNotFoundError(f"Partial {partial_name} not found")
            if not (self.env.partials_dir / partial_name).exists():
                raise PartialNotFoundError(f"Partial {partial_name} not found")
            os.remove(self.env.partials_dir / partial_name)
            del self.nodes[partial_name]
        finally:
            self._initialized = True
