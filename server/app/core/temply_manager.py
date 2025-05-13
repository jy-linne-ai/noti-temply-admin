"""템플릿 파일 관리 모듈

이 모듈은 템플릿 파일들의 생성, 수정, 삭제 등의 파일 시스템 작업을 담당합니다.
"""

import shutil
from pathlib import Path
from typing import List, Optional

from app.core.config import TEMPLATES_DIR
from app.core.exceptions import TemplateError


class TemplyManager:
    """템플릿 파일 관리 클래스

    템플릿 파일들의 생성, 수정, 삭제 등의 파일 시스템 작업을 담당합니다.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """템플릿 파일 관리자 초기화

        Args:
            base_dir: 템플릿 파일의 기본 디렉토리. 기본값은 TEMPLATES_DIR
        """
        self.base_dir = Path(base_dir or TEMPLATES_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_template_path(self, template_id: str) -> Path:
        """템플릿 파일의 전체 경로를 반환

        Args:
            template_id: 템플릿 ID

        Returns:
            Path: 템플릿 파일의 전체 경로
        """
        return self.base_dir / f"{template_id}.html"

    def create_template(self, template_id: str, content: str) -> None:
        """새로운 템플릿 파일 생성

        Args:
            template_id: 템플릿 ID
            content: 템플릿 내용

        Raises:
            TemplateError: 템플릿 파일이 이미 존재하는 경우
        """
        template_path = self.get_template_path(template_id)
        if template_path.exists():
            raise TemplateError(f"템플릿 파일이 이미 존재합니다: {template_id}")

        template_path.write_text(content, encoding="utf-8")

    def update_template(self, template_id: str, content: str) -> None:
        """기존 템플릿 파일 수정

        Args:
            template_id: 템플릿 ID
            content: 새로운 템플릿 내용

        Raises:
            TemplateError: 템플릿 파일이 존재하지 않는 경우
        """
        template_path = self.get_template_path(template_id)
        if not template_path.exists():
            raise TemplateError(f"템플릿 파일이 존재하지 않습니다: {template_id}")

        template_path.write_text(content, encoding="utf-8")

    def delete_template(self, template_id: str) -> None:
        """템플릿 파일 삭제

        Args:
            template_id: 템플릿 ID

        Raises:
            TemplateError: 템플릿 파일이 존재하지 않는 경우
        """
        template_path = self.get_template_path(template_id)
        if not template_path.exists():
            raise TemplateError(f"템플릿 파일이 존재하지 않습니다: {template_id}")

        template_path.unlink()

    def get_template_content(self, template_id: str) -> str:
        """템플릿 파일의 내용을 읽어옴

        Args:
            template_id: 템플릿 ID

        Returns:
            str: 템플릿 내용

        Raises:
            TemplateError: 템플릿 파일이 존재하지 않는 경우
        """
        template_path = self.get_template_path(template_id)
        if not template_path.exists():
            raise TemplateError(f"템플릿 파일이 존재하지 않습니다: {template_id}")

        return template_path.read_text(encoding="utf-8")

    def list_templates(self) -> List[str]:
        """모든 템플릿 ID 목록을 반환

        Returns:
            List[str]: 템플릿 ID 목록
        """
        return [f.stem for f in self.base_dir.glob("*.html")]

    def template_exists(self, template_id: str) -> bool:
        """템플릿 파일의 존재 여부를 확인

        Args:
            template_id: 템플릿 ID

        Returns:
            bool: 템플릿 파일이 존재하면 True, 아니면 False
        """
        return self.get_template_path(template_id).exists()

    def backup_template(self, template_id: str) -> None:
        """템플릿 파일을 백업

        Args:
            template_id: 템플릿 ID

        Raises:
            TemplateError: 템플릿 파일이 존재하지 않는 경우
        """
        template_path = self.get_template_path(template_id)
        if not template_path.exists():
            raise TemplateError(f"템플릿 파일이 존재하지 않습니다: {template_id}")

        backup_path = template_path.with_suffix(".html.bak")
        shutil.copy2(template_path, backup_path)

    def restore_template(self, template_id: str) -> None:
        """백업된 템플릿 파일을 복원

        Args:
            template_id: 템플릿 ID

        Raises:
            TemplateError: 백업 파일이 존재하지 않는 경우
        """
        template_path = self.get_template_path(template_id)
        backup_path = template_path.with_suffix(".html.bak")

        if not backup_path.exists():
            raise TemplateError(f"백업 파일이 존재하지 않습니다: {template_id}")

        shutil.copy2(backup_path, template_path)
