"""Temply 환경"""

import json
import re
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Set

from jinja2 import Environment, FileSystemLoader, PrefixLoader, StrictUndefined, Template, nodes
from jinja2schema.model import Dictionary  # type: ignore
from markupsafe import escape

from temply_app.core.config import Config
from temply_app.core.temply.parser.meta_model import JST, BaseMetaData
from temply_app.core.temply.schema.generator import infer_from_ast, to_json_schema
from temply_app.core.temply.schema.mergers import merge
from temply_app.core.temply.schema.utils import generate_object


class TemplateComponents(str, Enum):
    """템플릿 아이템"""

    TEXT_EMAIL_SUBJECT = "TEXT_EMAIL_SUBJECT"
    HTML_EMAIL = "HTML_EMAIL"
    TEXT_EMAIL = "TEXT_EMAIL"
    TEXT_WEBPUSH_TITLE = "TEXT_WEBPUSH_TITLE"
    TEXT_WEBPUSH_URL = "TEXT_WEBPUSH_URL"
    TEXT_WEBPUSH = "TEXT_WEBPUSH"


class TemplyEnv:
    """Temply 환경"""

    def __init__(
        self,
        config: Config,
        version: str | None = None,
        pr_version: str | None = None,
    ):
        self._config: Config = config
        self.version: str | None = version
        self.pr_version: str | None = pr_version
        self.applied_version: str | None = None
        if config.is_dev() and pr_version:
            self.applied_version = pr_version
        else:
            self.applied_version = version

        self.templates_dir: Path
        self.templates_dir_name: str = "templates"

        self.layouts_dir: Path
        self.layouts_dir_name: str = "layouts"

        self.partials_dir: Path
        self.partials_dir_name: str = "partials"

        self.schema_filename: str = "schema.json"
        self.file_encoding: str = config.file_encoding

        if not (Path(str(self._config.noti_temply_dir))).exists():
            raise FileNotFoundError(f"path {self._config.noti_temply_dir} not found")

        if self.applied_version:
            self.templates_dir = (
                Path(str(self._config.noti_temply_dir))
                / self.applied_version
                / self.templates_dir_name
            )
            self.layouts_dir = (
                Path(str(self._config.noti_temply_dir))
                / self.applied_version
                / self.layouts_dir_name
            )
            self.partials_dir = (
                Path(str(self._config.noti_temply_dir))
                / self.applied_version
                / self.partials_dir_name
            )
        else:

            self.templates_dir = Path(str(self._config.noti_temply_dir)) / self.templates_dir_name
            self.layouts_dir = Path(str(self._config.noti_temply_dir)) / self.layouts_dir_name
            self.partials_dir = Path(str(self._config.noti_temply_dir)) / self.partials_dir_name

        if not self.templates_dir.exists():
            if config.is_local():
                self.templates_dir.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(f"path {self.templates_dir} not found")
        if not self.layouts_dir.exists():
            if config.is_local():
                self.layouts_dir.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(f"path {self.layouts_dir} not found")
        if not self.partials_dir.exists():
            if config.is_local():
                self.partials_dir.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(f"path {self.partials_dir} not found")

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
            auto_reload=self._config.is_dev(),
        )
        _env.filters.update(filters)
        return _env

    def load_schema_source(self, template_name: str) -> dict[str, Any]:
        """스키마 소스 조회"""
        schema_path = self.templates_dir / template_name / self.schema_filename
        if not schema_path.exists():
            return {}
        with open(
            schema_path,
            "r",
            encoding=self.file_encoding,
        ) as f:
            return json.loads(f.read())

    def load_source(self, component_path: str) -> tuple[str, str | None, Callable[[], bool] | None]:
        """템플릿 컴포넌트 소스 조회"""
        if not self.env.loader:
            raise ValueError("Template loader is not initialized")
        return self.env.loader.get_source(self.env, component_path)

    def load_layout_source(
        self, layout_name: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        """템플릿 소스 경로 조회"""
        return self.load_source(self.build_layout_path(layout_name))

    def load_partial_source(
        self, partial_name: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        """파트 소스 경로 조회"""
        return self.load_source(self.build_partial_path(partial_name))

    def load_component_source(
        self, template_name: str, component_name: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        """템플릿 소스 경로 조회"""
        return self.load_source(self.build_component_path(template_name, component_name))

    # def get_layout_template(self, layout_name: str) -> Template:
    #     """레이아웃 조회"""
    #     return self.env.get_template(self._build_layout_path(layout_name))

    # def get_partial_template(self, partial_name: str) -> Template:
    #     """파트 조회"""
    #     return self.env.get_template(self._build_partial_path(partial_name))

    def get_component_template(self, template_name: str, component_name: str) -> Template:
        """템플릿 조회"""
        return self.env.get_template(self.build_component_path(template_name, component_name))

    def parse(self, content: str) -> nodes.Template:
        """템플릿 파싱"""
        return self.env.parse(content)

    # def parse_layout(self, layout_name: str) -> nodes.Template:
    #     """레이아웃 파싱"""
    #     content, _, _ = self.load_layout_source(layout_name)
    #     return self.parse(content)

    # def parse_partial(self, partial_name: str) -> nodes.Template:
    #     """파트 파싱"""
    #     content, _, _ = self.load_partial_source(partial_name)
    #     return self.parse(content)

    def parse_component(self, template_name: str, component_name: str) -> nodes.Template:
        """템플릿 컴포넌트 파싱"""
        content, _, _ = self.load_component_source(template_name, component_name)
        return self.parse(content)

    def _source_parse_component(self, template_name: str, component_name: str) -> Any:
        """템플릿 컴포넌트 소스 파싱"""
        content, _, _ = self.load_component_source(template_name, component_name)
        return self.parse(content)

    def get_template_names(self) -> list[str]:
        """템플릿 목록 조회"""
        items: list[str] = []
        for item in self.templates_dir.iterdir():
            if item.is_file() or item.name.startswith("."):  # .DS_Store 파일 제외
                continue
            items.append(item.name)
        return items

    def get_component_names(self, template_name: str) -> list[str]:
        """템플릿 컴포넌트 목록 조회"""
        components: list[str] = []
        template_dir = self.templates_dir / template_name
        if not template_dir.exists():
            raise ValueError(f"Template {template_name} not found")

        for item in template_dir.iterdir():
            if not item.is_file():
                continue
            if item.name.startswith("."):  # .DS_Store 파일 제외
                continue
            if item.suffix == ".json":  # 스키마 파일 제외
                continue
            components.append(item.name)
        return components

    def get_template_schema(self, template_name: str) -> Dict[str, Any]:
        """템플릿 컴포넌트 스키마 조회"""
        params = Dictionary()
        for component_name in self.get_component_names(template_name):
            ast = self._source_parse_component(template_name, component_name)
            rv = infer_from_ast(ast, self.env)
            params = merge(params, rv)
        return to_json_schema(params)

    def get_template_schema_generator(self, template_name: str) -> Dict[str, Any]:
        """템플릿 컴포넌트 스키마 생성기 조회"""
        return generate_object(self.load_schema_source(template_name))

    def render_component(
        self, template_name: str, component_name: str, schema_data: Dict[str, Any]
    ) -> str:
        """템플릿 컴포넌트 렌더링"""
        return self.get_component_template(template_name, component_name).render(schema_data)

    def render_template(self, template_name: str, schema_data: Dict[str, Any]) -> Dict[str, str]:
        """템플릿 컴포넌트 렌더링"""
        result = dict()
        for component_name in self.get_component_names(template_name):
            result[component_name] = self.render_component(
                template_name, component_name, schema_data
            )
        return result

    def _build_template_path(self, template_name: str) -> str:
        """템플릿 경로 조회"""
        return self.templates_dir_name + "/" + template_name

    def build_component_path(self, template_name: str, component_name: str) -> str:
        """템플릿 컴포넌트 경로 조회"""
        return self._build_template_path(template_name) + "/" + component_name

    def build_component_schema_path(self, template_name: str) -> str:
        """템플릿 컴포넌트 스키마 경로 조회"""
        return self._build_template_path(template_name) + "/" + self.schema_filename

    def get_layout_names(self) -> list[str]:
        """레이아웃 목록 조회"""
        items: list[str] = []
        for item in self.layouts_dir.iterdir():
            if not item.is_file():
                continue
            items.append(item.name)
        return items

    def build_layout_path(self, layout_name: str) -> str:
        """레이아웃 경로 조회"""
        return self.layouts_dir_name + "/" + layout_name

    def get_partial_names(self) -> list[str]:
        """파트 목록 조회"""
        items: list[str] = []
        for item in self.partials_dir.iterdir():
            if not item.is_file():
                continue
            items.append(item.name)
        return items

    def build_partial_path(self, partial_name: str) -> str:
        """파트 경로 조회"""
        return self.partials_dir_name + "/" + partial_name

    def _get_import_name(self, name: str) -> str:
        """Get template name."""
        return name.replace("/", "_").replace("-", "_")

    def format_partial_imports(self, partial_names: Set[str]) -> list[str]:
        """Make partials in Jinja format."""
        result = []
        for partial_name in partial_names:
            result.append(
                f"{{%- from '{self.partials_dir_name}/{partial_name}' import render as {self._get_import_name(partial_name)} with context -%}}"
            )
        return result

    def format_meta_block(self, meta: BaseMetaData) -> str:
        """Make meta in Jinja format."""
        lines = ["{#-"]

        description = meta.description.replace("\n", "\\n") if meta.description else ""
        lines.append(f"description: {description}")
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

    def format_layout_block(self, layout_name: str) -> str:
        """Make layout in Jinja format."""
        return f"{{%- extends '{self.layouts_dir_name}/{layout_name}' -%}}"

    def format_layout_content(self, layout_content: str) -> str:
        """Make layout body in Jinja format."""
        return f"{{%- block content -%}}\n{layout_content}\n{{%- endblock -%}}"

    def format_partial_content(self, partial_content: str) -> str:
        """Make partial body in Jinja format."""
        return f"{{%- macro render(locals = {{}}) -%}}\n{partial_content}\n{{%- endmacro -%}}"

    # def get_template_component_body_jinja_format(self, content: str) -> str:
    #     """Make template body in Jinja format."""
    #     return f"{{%- block content -%}}\n{content}\n{{%- endblock -%}}"

    def validate_file_name(self, file_name: str) -> bool:
        """템플릿 이름이 유효한지 검사합니다.

        Args:
            template: 검사할 템플릿 이름

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

    def validate_component_name(self, component_name: str) -> bool:
        """템플릿 컴포넌트 이름이 유효한지 검사합니다.

        Args:
            template: 검사할 템플릿 이름
            component: 검사할 템플릿 컴포넌트 이름

        Returns:
            bool: 템플릿 이름이 유효하면 True, 아니면 False
        """
        if not component_name:
            return False
        if not self.validate_file_name(component_name):
            return False
        if component_name not in TemplateComponents.__members__:
            return False
        return True
