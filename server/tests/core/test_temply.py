"""템플릿 파싱 테스트"""

import copy
import difflib
import json
import pprint
import re
from pathlib import Path
from typing import Any, List

import pytest
from jinja2 import Environment, FileSystemLoader, PrefixLoader, StrictUndefined
from jinja2schema.model import Dictionary  # type: ignore
from jsonschema import validate
from jsonschema.validators import RefResolver
from markupsafe import escape

from app.core.temply.schema import get_mode_title, infer_from_ast, to_json_schema
from app.core.temply.schema.mergers import merge
from app.core.temply.schema.schema_parser import normalize_ref, remove_namespace
from app.core.temply.schema.utils import generate_object


def environment_options() -> tuple[dict[str, Any], dict[str, Any]]:
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


def get_base_path() -> Path:
    """테스트 데이터 경로"""
    base = Path(__file__).parent.parent / "data"
    return base


# class CustomPreFixLoader(PrefixLoader):
#     """템플릿 로더 커스텀"""

#     def get_source(
#         self, environment, template
#     ) -> tuple[str, str | None, Callable[[], bool] | None]:
#         """템플릿 로더 커스텀"""
#         try:
#             if not template.endswith(".j2"):
#                 return super().get_source(environment, f"{template}.j2")
#             else:
#                 return super().get_source(environment, template)
#         except TemplateNotFound:
#             if not template.endswith(".j2"):
#                 return super().get_source(environment, template)
#             raise


@pytest.mark.asyncio
def template_names() -> List[str]:
    """템플릿 이름 추출"""
    base_path = get_base_path()
    match_template_files = []
    for file_path in (base_path / "templates").iterdir():
        if file_path.is_file():
            continue
        if file_path.name.startswith("."):
            continue
        match_template_files.append(file_path.name)
    return match_template_files


@pytest.mark.asyncio
def _get_template_item_names(root_path: Path, template_dir_name: str) -> List[str]:
    """템플릿 이름 추출"""
    match_template_files = []
    template_path = root_path / "templates" / template_dir_name
    print(root_path)
    print(template_path)
    for file_path in template_path.iterdir():
        if file_path.is_dir() or file_path.name.endswith(".json") or file_path.name.startswith("."):
            continue
        match_template_files.append(f"templates/{template_dir_name}/{file_path.name}")
    return match_template_files


@pytest.fixture
def v_env():
    """테스트 환경 설정"""
    kwargs, filters = environment_options()
    base_path = get_base_path()
    _env = Environment(
        loader=PrefixLoader(
            {
                "templates": FileSystemLoader(str(base_path / "templates")),
                "layouts": FileSystemLoader(str(base_path / "layouts")),
                "partials": FileSystemLoader(str(base_path / "partials")),
            }
        ),
        **kwargs,
    )
    _env.filters.update(filters)
    return _env


@pytest.mark.asyncio
@pytest.mark.parametrize("template_name", template_names())
# pylint: disable=redefined-outer-name
def test_schema_equal(v_env, template_name):
    """모든 템플릿 파싱 테스트"""
    base_path = get_base_path()
    # template_name = "arrangement_mailer"
    # template_name = "arrangement_mailer:receive_message"
    match_template_files = _get_template_item_names(base_path, template_name)
    params = Dictionary()

    for template_file_path in match_template_files:
        # templates/arrangement_mailer/... 형식으로 템플릿 로드
        print(template_file_path)
        content, _, _ = v_env.loader.get_source(v_env, template_file_path)
        ast = v_env.parse(content)
        rv = infer_from_ast(ast, v_env)
        params = merge(params, rv)
        print(template_file_path)
    # CustomSchemaGenerator 사용
    json_schema = to_json_schema(params)

    # 파싱된 결과를 schema-test.json으로 저장
    test_schema_path = base_path / "templates" / template_name / "schema-test.json"
    with open(test_schema_path, "w", encoding="utf-8") as f:
        json.dump(json_schema, f, indent=2, ensure_ascii=False)

    # 기대 스키마 로드
    schema_path = base_path / "templates" / template_name / "schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        expected_schema = json.load(f)

    expected_keys = set(expected_schema["properties"].keys())
    actual_keys = set(json_schema["properties"].keys())

    print(f"\n=== {template_name} 전체 템플릿 변수 차이 분석 ===")
    print("실제 결과(parsed)에만 있는 변수:", actual_keys - expected_keys)
    print("기대 결과(expected)에만 있는 변수:", expected_keys - actual_keys)
    print("공통 변수:", actual_keys & expected_keys)
    print("===================\n")

    # properties의 키가 일치하는지 확인
    assert actual_keys == expected_keys

    # $defs의 내용이 일치하는지 확인 (키 이름은 무시)
    def normalize_defs(schema):
        defs = schema.get("$defs", {})
        normalized = {}
        for k, v in defs.items():
            v = copy.deepcopy(v)
            v = fix_refs(v)
            normalized[k.split(".")[-1]] = v
        return normalized

    def fix_refs(obj):
        if isinstance(obj, dict):
            return {
                k: (
                    fix_refs(v)
                    if not (k == "$ref" and isinstance(v, str) and v.startswith("#/$defs/"))
                    else "#/$defs/" + v.split("/")[-1]
                )
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [fix_refs(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("#/$defs/"):
            return "#/$defs/" + obj.split("/")[-1]
        return obj

    actual_defs = normalize_defs(json_schema)
    expected_defs = normalize_defs(expected_schema)

    if actual_defs != expected_defs:
        print("\n[DIFF] actual_defs vs expected_defs:")
        actual_str = pprint.pformat(actual_defs, width=120, compact=True, sort_dicts=True)
        expected_str = pprint.pformat(expected_defs, width=120, compact=True, sort_dicts=True)
        diff = difflib.unified_diff(
            expected_str.splitlines(),
            actual_str.splitlines(),
            fromfile="expected_defs",
            tofile="actual_defs",
            lineterm="",
        )
        print("\n".join(diff))
    assert actual_defs == expected_defs

    # 나머지 속성들이 일치하는지 확인
    actual_schema = json_schema.copy()
    expected_schema_copy = expected_schema.copy()
    del actual_schema["$defs"]
    del expected_schema_copy["$defs"]
    if actual_schema != expected_schema_copy:
        print("\n[DIFF] actual_schema vs expected_schema:")
        actual_str = pprint.pformat(actual_schema, width=120, compact=True, sort_dicts=True)
        expected_str = pprint.pformat(
            expected_schema_copy, width=120, compact=True, sort_dicts=True
        )
        diff = difflib.unified_diff(
            expected_str.splitlines(),
            actual_str.splitlines(),
            fromfile="expected_schema",
            tofile="actual_schema",
            lineterm="",
        )
        print("\n".join(diff))
    assert actual_schema == expected_schema_copy


@pytest.mark.asyncio
def test_get_mode_title():
    """모드 제목 테스트"""

    assert get_mode_title("input") == "Input"
    assert get_mode_title("output") == "Output"
    assert get_mode_title("other") == "Output"  # 기본값


@pytest.mark.asyncio
@pytest.mark.parametrize("template_name", template_names())
# pylint: disable=redefined-outer-name
def test_schema_validate_with_random_data(template_name):
    """템플릿 스키마 검증 테스트"""
    base_path = get_base_path()
    schema_path = base_path / "templates" / template_name / "schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    schema_data = generate_object(schema)

    # 생성된 데이터로 스키마 검증
    resolver = RefResolver.from_schema(schema)
    validate(instance=schema_data, schema=schema, resolver=resolver)


@pytest.mark.asyncio
@pytest.mark.parametrize("template_name", template_names())
def test_parse_content(v_env, template_name):
    """템플릿 파싱 테스트"""
    base_path = get_base_path()
    schema_path = base_path / "templates" / template_name / "schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    schema_data = generate_object(schema)

    match_template_files = _get_template_item_names(base_path, template_name)
    for template_file_path in match_template_files:
        print(template_file_path)
        template = v_env.get_template(template_file_path)
        print(template.render(schema_data))
