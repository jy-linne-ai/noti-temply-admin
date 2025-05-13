import json
from pathlib import Path
from typing import Dict, List, Optional

import jinja2

from ..core.config import CONTENT_FILE, FILE_ENCODING, INFO_FILE, PARTIALS_DIR, SCHEMA_FILE


class PartialService:
    def __init__(self):
        self.loader = jinja2.FileSystemLoader(str(PARTIALS_DIR))
        self.env = jinja2.Environment(loader=self.loader)

    def _get_partial_dir(self, partial_id: str) -> Path:
        """파셜 디렉토리 경로를 반환합니다."""
        return PARTIALS_DIR / partial_id

    def list_partials(self, parent_id: Optional[str] = None) -> List[Dict]:
        """모든 파셜 목록을 반환합니다."""
        partials = []
        for partial_dir in PARTIALS_DIR.iterdir():
            if not partial_dir.is_dir():
                continue

            info_path = partial_dir / INFO_FILE
            if not info_path.exists():
                continue

            with open(info_path, "r", encoding=FILE_ENCODING) as f:
                info = json.load(f)
                if parent_id is not None and info.get("parent_id") != parent_id:
                    continue
                partials.append({"id": partial_dir.name, **info})

        return partials

    def get_partial(self, partial_id: str) -> Optional[Dict]:
        """파셜 정보를 반환합니다."""
        partial_dir = self._get_partial_dir(partial_id)
        if not partial_dir.exists():
            return None

        info_path = partial_dir / INFO_FILE
        schema_path = partial_dir / SCHEMA_FILE
        content_path = partial_dir / CONTENT_FILE

        if not all(p.exists() for p in [info_path, schema_path, content_path]):
            return None

        with open(info_path, "r", encoding=FILE_ENCODING) as f:
            info = json.load(f)
        with open(schema_path, "r", encoding=FILE_ENCODING) as f:
            schema = json.load(f)
        with open(content_path, "r", encoding=FILE_ENCODING) as f:
            content = f.read()

        return {"id": partial_id, **info, "schema": schema, "content": content}

    def get_children(self, partial_id: str) -> List[Dict]:
        """자식 파셜 목록을 반환합니다."""
        return self.list_partials(parent_id=partial_id)

    def get_parent(self, partial_id: str) -> Optional[Dict]:
        """부모 파셜 정보를 반환합니다."""
        partial = self.get_partial(partial_id)
        if not partial or "parent_id" not in partial:
            return None
        return self.get_partial(partial["parent_id"])

    def create_partial(self, partial_id: str, info: Dict, schema_data: Dict, content: str) -> bool:
        """새로운 파셜을 생성합니다."""
        partial_dir = self._get_partial_dir(partial_id)
        if partial_dir.exists():
            return False

        # 부모 파셜이 존재하는지 확인
        if "parent_id" in info:
            parent = self.get_partial(info["parent_id"])
            if not parent:
                return False

        partial_dir.mkdir(parents=True)

        with open(partial_dir / INFO_FILE, "w", encoding=FILE_ENCODING) as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        with open(partial_dir / SCHEMA_FILE, "w", encoding=FILE_ENCODING) as f:
            json.dump(schema_data, f, ensure_ascii=False, indent=2)
        with open(partial_dir / CONTENT_FILE, "w", encoding=FILE_ENCODING) as f:
            f.write(content)

        return True

    def update_partial(self, partial_id: str, info: Dict, schema_data: Dict, content: str) -> bool:
        """파셜을 업데이트합니다."""
        partial_dir = self._get_partial_dir(partial_id)
        if not partial_dir.exists():
            return False

        # 부모 파셜이 존재하는지 확인
        if "parent_id" in info:
            parent = self.get_partial(info["parent_id"])
            if not parent:
                return False

        with open(partial_dir / INFO_FILE, "w", encoding=FILE_ENCODING) as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        with open(partial_dir / SCHEMA_FILE, "w", encoding=FILE_ENCODING) as f:
            json.dump(schema_data, f, ensure_ascii=False, indent=2)
        with open(partial_dir / CONTENT_FILE, "w", encoding=FILE_ENCODING) as f:
            f.write(content)

        return True

    def delete_partial(self, partial_id: str) -> bool:
        """파셜을 삭제합니다."""
        partial_dir = self._get_partial_dir(partial_id)
        if not partial_dir.exists():
            return False

        # 자식 파셜이 있는지 확인
        children = self.get_children(partial_id)
        if children:
            return False

        for file in partial_dir.iterdir():
            file.unlink()
        partial_dir.rmdir()

        return True

    def render_partial(self, partial_id: str, variables: Dict) -> str:
        """파셜을 렌더링합니다."""
        template = self.env.get_template(f"{partial_id}/{CONTENT_FILE}")
        return template.render(**variables)
