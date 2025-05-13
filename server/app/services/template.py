import json
from pathlib import Path
from typing import Dict, List, Optional

import jinja2

from ..core.config import CONTENT_FILE, FILE_ENCODING, SCHEMA_FILE, TEMPLATES_DIR
from .layout import LayoutService
from .partial import PartialService


class TemplateService:
    def __init__(self):
        self.loader = jinja2.FileSystemLoader(str(TEMPLATES_DIR))
        self.env = jinja2.Environment(loader=self.loader)
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    def _get_template_dir(self, template_id: str) -> Path:
        """템플릿 디렉토리 경로를 반환합니다."""
        return TEMPLATES_DIR / template_id

    def list_templates(self) -> List[Dict]:
        """모든 템플릿 목록을 반환합니다."""
        templates = []
        for template_dir in TEMPLATES_DIR.iterdir():
            if not template_dir.is_dir():
                continue

            info_path = template_dir / INFO_FILE
            if not info_path.exists():
                continue

            with open(info_path, "r", encoding=FILE_ENCODING) as f:
                info = json.load(f)
                templates.append({"id": template_dir.name, **info})

        return templates

    def get_template(self, template_id: str) -> Optional[Dict]:
        """템플릿 정보를 반환합니다."""
        template_dir = self._get_template_dir(template_id)
        if not template_dir.exists():
            return None

        info_path = template_dir / INFO_FILE
        schema_path = template_dir / SCHEMA_FILE
        content_path = template_dir / CONTENT_FILE

        if not all(p.exists() for p in [info_path, schema_path, content_path]):
            return None

        with open(info_path, "r", encoding=FILE_ENCODING) as f:
            info = json.load(f)
        with open(schema_path, "r", encoding=FILE_ENCODING) as f:
            schema = json.load(f)
        with open(content_path, "r", encoding=FILE_ENCODING) as f:
            content = f.read()

        return {"id": template_id, **info, "schema": schema, "content": content}

    def create_template(self, template_id: str, info: Dict, schema: Dict, content: str) -> bool:
        """새로운 템플릿을 생성합니다."""
        template_dir = self._get_template_dir(template_id)
        if template_dir.exists():
            return False

        template_dir.mkdir(parents=True)

        with open(template_dir / INFO_FILE, "w", encoding=FILE_ENCODING) as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        with open(template_dir / SCHEMA_FILE, "w", encoding=FILE_ENCODING) as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
        with open(template_dir / CONTENT_FILE, "w", encoding=FILE_ENCODING) as f:
            f.write(content)

        return True

    def update_template(self, template_id: str, info: Dict, schema: Dict, content: str) -> bool:
        """템플릿을 업데이트합니다."""
        template_dir = self._get_template_dir(template_id)
        if not template_dir.exists():
            return False

        with open(template_dir / INFO_FILE, "w", encoding=FILE_ENCODING) as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        with open(template_dir / SCHEMA_FILE, "w", encoding=FILE_ENCODING) as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
        with open(template_dir / CONTENT_FILE, "w", encoding=FILE_ENCODING) as f:
            f.write(content)

        return True

    def delete_template(self, template_id: str) -> bool:
        """템플릿을 삭제합니다."""
        template_dir = self._get_template_dir(template_id)
        if not template_dir.exists():
            return False

        for file in template_dir.iterdir():
            file.unlink()
        template_dir.rmdir()

        return True

    def preview_template(self, template_id: str, variables: Dict) -> Optional[str]:
        """템플릿을 미리보기합니다."""
        template = self.get_template(template_id)
        if not template:
            return None

        try:
            # 레이아웃이 있는 경우 레이아웃에 내용을 삽입
            if "layout" in template:
                layout_obj = self.env.from_string(template["layout"])
                content_obj = self.env.from_string(template["content"])
                content = content_obj.render(**variables)
                return layout_obj.render(content=content, **variables)
            else:
                # 레이아웃이 없는 경우 내용만 렌더링
                template_obj = self.env.from_string(template["content"])
                return template_obj.render(**variables)
        except Exception as e:
            print(f"Error rendering template: {e}")
            return None

    def render_template(self, template_id: str, variables: Dict) -> str:
        """템플릿을 렌더링합니다."""
        template = self.env.get_template(f"{template_id}/{CONTENT_FILE}")
        return template.render(**variables)
