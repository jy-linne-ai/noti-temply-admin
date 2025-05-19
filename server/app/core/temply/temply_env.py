"""Temply 환경"""

import re
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Set

from jinja2 import Environment, FileSystemLoader, PrefixLoader, StrictUndefined, Template, nodes
from jinja2schema.model import Dictionary  # type: ignore
from markupsafe import escape

from app.core.config import Config
from app.core.temply.parser.meta_model import JST, BaseMetaData
from app.core.temply.schema.generator import infer_from_ast, to_json_schema
from app.core.temply.schema.mergers import merge


class TemplateItems(str, Enum):
    """템플릿 아이템"""

    HTML_EMAIL = "HTML_EMAIL"
    TEXT_EMAIL = "TEXT_EMAIL"
    TEXT_WEBPUSH = "TEXT_WEBPUSH"
    TEXT_EMAIL_SUBJECT = "TEXT_EMAIL_SUBJECT"
    TEXT_WEBPUSH_TITLE = "TEXT_WEBPUSH_TITLE"
    TEXT_WEBPUSH_URL = "TEXT_WEBPUSH_URL"


class TemplyEnv:
    """Temply 환경"""

    def __init__(self, config: Config, version: str | None = None):
        self._config: Config = config
        self.version: str | None = version
        self.templates_dir: Path
        self.layouts_dir: Path
        self.partials_dir: Path
        self.partials_dir_name: str = "partials"
        self.layouts_dir_name: str = "layouts"
        self.templates_dir_name: str = "templates"
        self.schema_file: str = "schema.json"
        self.file_encoding: str = config.file_encoding

        if not (Path(str(self._config.noti_temply_dir))).exists():
            raise FileNotFoundError(f"path {self._config.noti_temply_dir} not found")

        if version:

            self.templates_dir = (
                Path(str(self._config.noti_temply_dir)) / version / self.templates_dir_name
            )
            self.layouts_dir = (
                Path(str(self._config.noti_temply_dir)) / version / self.layouts_dir_name
            )
            self.partials_dir = (
                Path(str(self._config.noti_temply_dir)) / version / self.partials_dir_name
            )
        else:

            self.templates_dir = Path(str(self._config.noti_temply_dir)) / self.templates_dir_name
            self.layouts_dir = Path(str(self._config.noti_temply_dir)) / self.layouts_dir_name
            self.partials_dir = Path(str(self._config.noti_temply_dir)) / self.partials_dir_name

        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
        if not self.layouts_dir.exists():
            self.layouts_dir.mkdir(parents=True, exist_ok=True)
        if not self.partials_dir.exists():
            self.partials_dir.mkdir(parents=True, exist_ok=True)

        self.env = self._get_env()

    def _environment_options(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """테스트 환경 설정"""

        def escape_nl2br(value: str) -> str:
            return "<br>\n".join(escape(line) for line in re.split(r"\r?\n", value))

        return {
            "undefined": StrictUndefined,
            "extensions": ["jinja2.ext.loopcontrols", "jinja2.ext.do"],
        }, {
            "escape_nl2br": escape_nl2br,
            "cache_size": 100,
        }

    def _get_env(self) -> Environment:
        """템플릿 환경 조회"""
        kwargs, filters = self._environment_options()
        _env = Environment(
            loader=PrefixLoader(
                {
                    "templates": FileSystemLoader(str(self.templates_dir)),
                    "layouts": FileSystemLoader(str(self.layouts_dir)),
                    "partials": FileSystemLoader(str(self.partials_dir)),
                }
            ),
            **kwargs,
            auto_reload=self._config.debug,
        )
        _env.filters.update(filters)
        return _env

    def get_source(
        self, template_file_path: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        """템플릿 소스 조회"""
        return self.env.loader.get_source(self.env, template_file_path)

    def get_source_layout(
        self, layout_file: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        """템플릿 소스 경로 조회"""
        return self.get_source(self._get_layout_path(layout_file))

    def get_source_partial(
        self, partial_file: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        """파트 소스 경로 조회"""
        return self.get_source(self._get_partial_path(partial_file))

    def get_source_template(
        self, category_name: str, template_file: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        """템플릿 소스 경로 조회"""
        return self.get_source(self._get_template_path(category_name, template_file))

    def get_template(self, template_file_path: str) -> Template:
        """템플릿 조회"""
        return self.env.get_template(template_file_path)

    def parse(self, content: str) -> nodes.Template:
        """템플릿 파싱"""
        return self.env.parse(content)

    def source_parse(self, template_file_path: str) -> Any:
        """템플릿 소스 파싱"""
        content, _, _ = self.get_source(template_file_path)
        return self.parse(content)

    def get_category_names(self) -> list[str]:
        """템플릿 카테고리 목록 조회"""
        items: list[str] = []
        for item in self.templates_dir.iterdir():
            if item.is_file() or item.name.startswith("."):  # .DS_Store 파일 제외
                continue
            items.append(item.name)
        return items

    def get_template_names(self, category: str) -> list[str]:
        """템플릿 목록 조회"""
        items: list[str] = []
        category_dir = self.templates_dir / category
        if not category_dir.exists():
            raise ValueError(f"Category {category} not found")

        for item in category_dir.iterdir():
            if not item.is_file():
                continue
            if item.name.startswith("."):  # .DS_Store 파일 제외
                continue
            if item.suffix == ".json":  # 스키마 파일 제외
                continue
            items.append(item.name)
        return items

    def get_category_schema(self, category: str) -> dict[str, Any]:
        """카테고리 스키마 조회"""
        params = Dictionary()
        for template_file_path in self.get_template_names(category):
            ast = self.source_parse(template_file_path)
            rv = infer_from_ast(ast, self.env)
            params = merge(params, rv)

        return to_json_schema(params)

    def _get_category_path(self, category: str) -> str:
        """카테고리 경로 조회"""
        return self.templates_dir_name + "/" + category

    def _get_template_path(self, category: str, name: str) -> str:
        """템플릿 경로 조회"""
        return self._get_category_path(category) + "/" + name

    def _get_template_schema_path(self, category: str) -> str:
        """템플릿 스키마 경로 조회"""
        return self._get_category_path(category) + "/" + self.schema_file

    def get_layout_names(self) -> list[str]:
        """레이아웃 목록 조회"""
        items: list[str] = []
        for item in self.layouts_dir.iterdir():
            if not item.is_file():
                continue
            items.append(item.name)
        return items

    def _get_layout_path(self, name: str) -> str:
        """레이아웃 경로 조회"""
        return self.layouts_dir_name + "/" + name

    def get_partial_names(self) -> list[str]:
        """파트 목록 조회"""
        items: list[str] = []
        for item in self.partials_dir.iterdir():
            if not item.is_file():
                continue
            items.append(item.name)
        return items

    def _get_partial_path(self, name: str) -> str:
        """파트 경로 조회"""
        return self.partials_dir_name + "/" + name

    def _get_import_name(self, template: str) -> str:
        """Get template name."""
        return template.replace("/", "_").replace("-", "_")

    def make_partials_jinja_format(self, partials: Set[str]) -> list[str]:
        """Make partials in Jinja format."""
        result = []
        for partial in partials:
            partial_name = f"{self.partials_dir_name}/{partial}"
            result.append(
                f"{{%- from '{partial_name}' import render as {self._get_import_name(partial_name)} with context -%}}"
            )
        return result

    def make_meta_jinja_format(self, meta: BaseMetaData) -> str:
        """Make meta in Jinja format."""
        lines = ["{#-"]

        lines.append(f"description: {meta.description or ''}")
        lines.append(
            # pylint: disable=line-too-long
            f"created_at: {meta.created_at.astimezone(JST).strftime('%Y-%m-%d %H:%M:%S') if meta.created_at else ''}"
        )
        lines.append(f"created_by: {meta.created_by or ''}")
        lines.append(
            # pylint: disable=line-too-long
            f"updated_at: {meta.updated_at.astimezone(JST).strftime('%Y-%m-%d %H:%M:%S') if meta.updated_at else ''}"
        )
        lines.append(f"updated_by: {meta.updated_by or ''}")
        lines.append("-#}")
        return "\n".join(lines)

    def make_layout_jinja_format(self, layout: str) -> str:
        """Make layout in Jinja format."""
        return f"{{%- extends '{self.layouts_dir_name}/{layout}' -%}}"

    def make_layout_body_jinja_format(self, content: str) -> str:
        """Make layout body in Jinja format."""
        return f"{{%- block content -%}}\n{content}\n{{%- endblock -%}}"

    def make_partial_body_jinja_format(self, content: str) -> str:
        """Make partial body in Jinja format."""
        return f"{{%- macro render(locals = {{}}) -%}}\n{content}\n{{%- endmacro -%}}"

    # def make_template_body_jinja_format(self, content: str) -> str:
    #     """Make template body in Jinja format."""
    #     return f"{{%- block content -%}}\n{content}\n{{%- endblock -%}}"

    def check_file_name(self, file_name: str) -> bool:
        """파일명이 유효한지 검사합니다.

        Args:
            file_name: 검사할 파일명

        Returns:
            bool: 파일명이 유효하면 True, 아니면 False
        """
        # 빈 문자열 체크
        if not file_name or not file_name.strip():
            return False

        # 숨김 파일, 시스템 파일, 임시 파일 제외
        if file_name.startswith((".", "~", "..")):
            return False

        # 파일명 길이 제한 (Windows MAX_PATH = 260)
        if len(file_name) > 255:
            return False

        # 파일명에 허용되지 않는 문자 포함 여부 확인
        # Windows: \ / : * ? " < > |
        # Unix: /
        # 공백
        invalid_chars = r'\/:*?"<>| '
        if any(char in file_name for char in invalid_chars):
            return False

        return True

    def check_template_name(self, template_name: str) -> bool:
        """템플릿 이름이 유효한지 검사합니다.

        Args:
            template_name: 검사할 템플릿 이름

        Returns:
            bool: 템플릿 이름이 유효하면 True, 아니면 False
        """
        if not template_name:
            return False
        if not self.check_file_name(template_name):
            return False
        if template_name not in TemplateItems.__members__:
            return False
        return True
