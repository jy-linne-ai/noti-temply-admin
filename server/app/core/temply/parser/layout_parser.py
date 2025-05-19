"""Layout parser module.

This module provides functionality to parse Jinja2 layouts.
"""

import asyncio
import os
from typing import List, Optional, Set

from app.core.exceptions import LayoutAlreadyExistsError, LayoutNotFoundError
from app.core.temply.parser.meta_model import BaseMetaData, LayoutMetaData
from app.core.temply.parser.meta_parser import MetaParser
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User


class LayoutParser:
    """Parser for Jinja2 layouts."""

    def __init__(self, temply_env: TemplyEnv):
        """Initialize the parser.

        Args:
            layouts_dir: Directory containing layout templates
        """
        self.env = temply_env
        self.nodes: dict[str, LayoutMetaData] = {}
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
            await self._build_layout_tree(await self._parse_layout_files())
            self._initialized = True

    async def _ensure_initialized(self):
        """초기화가 완료될 때까지 기다립니다."""
        if not self._initialized:
            if self._init_task is not None:
                await self._init_task
            else:
                await self._initialize()

    async def _parse_layout(self, layout_name: str) -> LayoutMetaData:
        """Parse a layout template.

        Args:
            layout_file: Path to the layout template

        Returns:
            LayoutMetaData: Parsed layout metadata
        """
        try:
            content, _, _ = self.env.get_source_layout(layout_name)
            meta, block = MetaParser.parse(content)
            return LayoutMetaData(
                name=layout_name,
                content=block.strip(),
                description=meta.description,
                created_at=meta.created_at,
                created_by=meta.created_by,
                updated_at=meta.updated_at,
                updated_by=meta.updated_by,
            )
        except FileNotFoundError as e:
            raise LayoutNotFoundError(f"Layout {layout_name} not found: {e}") from e

    async def _parse_layout_files(self) -> List[LayoutMetaData]:
        """Parse layout files and extract metadata.

        Returns:
            List[LayoutMetaData]: List of layout metadata
        """
        layouts = []
        for layout_name in self.env.get_layout_names():
            layouts.append(await self._parse_layout(layout_name))
        return layouts

    async def _build_layout_tree(self, layouts: List[LayoutMetaData]) -> None:
        """Build the layout tree.

        Returns:
            Dictionary mapping layout names to their nodes
        """
        for layout in layouts:
            self.nodes[layout.name] = layout

    async def print_layout_tree(
        self,
        node: Optional[LayoutMetaData] = None,
        level: int = 0,
        visited: Optional[Set[str]] = None,
    ) -> None:
        """Print the layout tree with detailed information.

        Args:
            node: Node to start printing from (defaults to root nodes)
            level: Current indentation level
            visited: Set of visited node names to prevent cycles
        """
        await self._ensure_initialized()

        if visited is None:
            visited = set()

        if node is None:
            print("\n=== 레이아웃 트리 구조 ===")
            for root in await self.get_layouts():
                await self.print_layout_tree(root, level, visited)
            return

        if node.name in visited:
            return

        visited.add(node.name)

        # 노드 정보 출력
        indent = "  " * level
        print(f"{indent}└─ {node.name}")

        print()  # 빈 줄로 구분

    async def get_layouts(self) -> List[LayoutMetaData]:
        """List all layouts.

        Returns:
            List of all layouts
        """
        await self._ensure_initialized()
        return list(self.nodes.values())

    async def get_layout(self, layout_name: str) -> LayoutMetaData:
        """Get a layout by name.

        Args:
            name: Name of the layout
        """
        await self._ensure_initialized()
        layout = self.nodes.get(layout_name)
        if layout is None:
            raise LayoutNotFoundError(f"Layout {layout_name} not found")
        return layout

    async def create(
        self, user: User, layout_name: str, content: str, description: Optional[str] = None
    ) -> LayoutMetaData:
        """Create a layout.

        Args:
            layout_name: Name of the layout
            content: Content of the layout
            meta: Metadata of the layout
        """
        await self._ensure_initialized()
        self._initialized = False
        try:
            if not self.env.check_file_name(layout_name):
                raise ValueError(f"Invalid layout name: {layout_name}")

            if layout_name in self.nodes:
                raise LayoutAlreadyExistsError(f"Layout {layout_name} already exists")
            if (self.env.layouts_dir / layout_name).exists():
                raise LayoutAlreadyExistsError(f"Layout {layout_name} already exists")

            meta = BaseMetaData(
                description=description,
                created_at=BaseMetaData.get_current_datetime(),
                created_by=user.name,
                updated_at=BaseMetaData.get_current_datetime(),
                updated_by=user.name,
            )

            await self._write_layout(layout_name, content, meta)

            self.nodes[layout_name] = await self._parse_layout(layout_name)
            return self.nodes[layout_name]
        finally:
            self._initialized = True

    async def _write_layout(self, layout_name: str, content: str, meta: BaseMetaData) -> None:
        """Write a layout.

        Args:
            layout_name: Name of the layout
            content: Content of the layout
            meta: Metadata of the layout
        """
        with open(self.env.layouts_dir / layout_name, "w", encoding=self.env.file_encoding) as f:
            f.write(self.env.make_meta_jinja_format(meta))
            f.write("\n")
            f.write(content)

    async def update(
        self, user: User, layout_name: str, content: str, description: Optional[str] = None
    ) -> LayoutMetaData:
        """Update a layout.

        Args:
            layout_name: Name of the layout
            content: Content of the layout
            meta: Metadata of the layout
        """
        await self._ensure_initialized()
        self._initialized = False
        try:
            if layout_name not in self.nodes:
                raise LayoutNotFoundError(f"Layout {layout_name} not found")

            if not (self.env.layouts_dir / layout_name).exists():
                raise LayoutNotFoundError(f"Layout {layout_name} not found")

            layout = await self.get_layout(layout_name)

            meta = BaseMetaData(
                description=description,
                created_at=layout.created_at,
                created_by=layout.created_by,
                updated_at=BaseMetaData.get_current_datetime(),
                updated_by=user.name,
            )

            await self._write_layout(layout_name, content, meta)

            self.nodes[layout_name] = await self._parse_layout(layout_name)
            return self.nodes[layout_name]
        finally:
            self._initialized = True

    async def delete(self, user: User, layout_name: str) -> None:
        """Delete a layout.

        Args:
            layout_name: Name of the layout
        """
        await self._ensure_initialized()
        self._initialized = False
        try:
            if layout_name not in self.nodes:
                raise LayoutNotFoundError(f"Layout {layout_name} not found")
            if not (self.env.layouts_dir / layout_name).exists():
                raise LayoutNotFoundError(f"Layout {layout_name} not found")

            os.remove(self.env.layouts_dir / layout_name)
            del self.nodes[layout_name]
        finally:
            self._initialized = True
