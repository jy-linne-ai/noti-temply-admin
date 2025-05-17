"""Layout parser module.

This module provides functionality to parse Jinja2 layouts.
"""

import asyncio
from typing import List, Optional, Set

from app.core.temply.metadata.meta_model import LayoutMetaData
from app.core.temply.metadata.meta_parser import parse_meta_from_content
from app.core.temply.temply_env import TemplyEnv


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
        self._init_task = asyncio.create_task(self._initialize())

    async def _initialize(self):
        """초기화 작업을 수행합니다."""
        await self._build_layout_tree(await self._parse_layout_files())
        self._initialized = True

    async def _ensure_initialized(self):
        """초기화가 완료될 때까지 기다립니다."""
        if not self._initialized:
            await self._init_task

    async def _parse_layout(self, layout_name: str) -> LayoutMetaData:
        """Parse a layout template.

        Args:
            layout_file: Path to the layout template

        Returns:
            LayoutMetaData: Parsed layout metadata
        """
        content, _, _ = self.env.get_source_layout(layout_name)
        meta = parse_meta_from_content(content)
        return LayoutMetaData(
            name=layout_name,
            content=content,
            description=meta.description,
            created_at=meta.created_at,
            created_by=meta.created_by,
            updated_at=meta.updated_at,
            updated_by=meta.updated_by,
        )

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

    async def get_layout(self, name: str) -> Optional[LayoutMetaData]:
        """Get a layout by name.

        Args:
            name: Name of the layout
        """
        await self._ensure_initialized()
        return self.nodes.get(name)
