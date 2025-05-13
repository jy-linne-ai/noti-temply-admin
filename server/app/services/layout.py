"""
레이아웃 서비스
"""

from typing import Dict, List, Optional

import jinja2

from ..core.config import LAYOUTS_DIR
from ..core.filesystem import FileSystem


class LayoutService:
    """레이아웃 관련 기능을 제공하는 서비스"""

    def __init__(self):
        """서비스 초기화"""
        self.fs = FileSystem()
        self.loader = jinja2.FileSystemLoader(str(LAYOUTS_DIR))
        self.env = jinja2.Environment(loader=self.loader)

    def list_layouts(self) -> List[Dict]:
        """모든 레이아웃 목록을 반환합니다."""
        return self.fs.list_files(LAYOUTS_DIR)

    def get_layout(self, layout_id: str) -> Optional[Dict]:
        """레이아웃 정보를 반환합니다."""
        return self.fs.get_file(LAYOUTS_DIR, layout_id)

    def create_layout(self, layout_id: str, info: Dict, schema: Dict, layout: str) -> bool:
        """새로운 레이아웃을 생성합니다."""
        return self.fs.create_file(LAYOUTS_DIR, layout_id, info, schema, layout)

    def update_layout(self, layout_id: str, info: Dict, schema: Dict, layout: str) -> bool:
        """레이아웃을 업데이트합니다."""
        return self.fs.update_file(LAYOUTS_DIR, layout_id, info, schema, layout)

    def delete_layout(self, layout_id: str) -> bool:
        """레이아웃을 삭제합니다."""
        return self.fs.delete_file(LAYOUTS_DIR, layout_id)

    def render_layout(self, layout_id: str, variables: Dict) -> str:
        """레이아웃을 렌더링합니다."""
        template = self.env.get_template(f"{layout_id}/content.jinja")
        return template.render(**variables)
