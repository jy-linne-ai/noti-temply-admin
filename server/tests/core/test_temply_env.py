"""TemplyEnv 테스트"""

import copy
import difflib
import json
import pprint
from pathlib import Path
from typing import List

import pytest
from jinja2 import TemplateNotFound
from jinja2schema.model import Dictionary  # type: ignore
from jsonschema import validate
from jsonschema.validators import RefResolver

from app.core.temply.parser.meta_model import BaseMetaData
from app.core.temply.schema.mergers import merge
from app.core.temply.schema.parser import get_mode_title
from app.core.temply.schema.utils import generate_object
from app.core.temply.temply_env import TemplateItems, TemplyEnv, infer_from_ast, to_json_schema


def get_base_path() -> Path:
    """테스트 데이터 경로"""
    base = Path(__file__).parent.parent / "data"
    return base


@pytest.mark.asyncio
def template_category_names() -> List[str]:
    """템플릿 카테고리 이름 추출"""
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
    # print(root_path)
    # print(template_path)
    for file_path in template_path.iterdir():
        if file_path.is_dir() or file_path.name.endswith(".json") or file_path.name.startswith("."):
            continue
        match_template_files.append(f"templates/{template_dir_name}/{file_path.name}")
    return match_template_files


@pytest.mark.asyncio
@pytest.mark.parametrize("template_category_name", template_category_names())
# pylint: disable=redefined-outer-name
def test_schema_equal(data_env, template_category_name):
    """모든 템플릿 파싱 테스트"""
    base_path = get_base_path()
    # template_name = "arrangement_mailer"
    # template_name = "arrangement_mailer:receive_message"
    match_template_files = _get_template_item_names(base_path, template_category_name)
    params = Dictionary()

    for template_file_path in match_template_files:
        # templates/arrangement_mailer/... 형식으로 템플릿 로드
        # print(template_file_path)
        ast = data_env.source_parse(template_file_path)
        rv = infer_from_ast(ast, data_env.env)
        params = merge(params, rv)
        # print(template_file_path)
    # CustomSchemaGenerator 사용
    json_schema = to_json_schema(params)

    # 파싱된 결과를 schema-test.json으로 저장
    test_schema_path = base_path / "templates" / template_category_name / "schema-test.json"
    with open(test_schema_path, "w", encoding="utf-8") as f:
        json.dump(json_schema, f, indent=2, ensure_ascii=False)

    # 기대 스키마 로드
    schema_path = base_path / "templates" / template_category_name / "schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        expected_schema = json.load(f)

    expected_keys = set(expected_schema["properties"].keys())
    actual_keys = set(json_schema["properties"].keys())

    print(f"\n=== {template_category_name} 전체 템플릿 변수 차이 분석 ===")
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
@pytest.mark.parametrize("template_category_name", template_category_names())
# pylint: disable=redefined-outer-name
def test_schema_validate_with_random_data(template_category_name):
    """템플릿 스키마 검증 테스트"""
    base_path = get_base_path()
    schema_path = base_path / "templates" / template_category_name / "schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    schema_data = generate_object(schema)

    # 생성된 데이터로 스키마 검증
    resolver = RefResolver.from_schema(schema)
    validate(instance=schema_data, schema=schema, resolver=resolver)


@pytest.mark.asyncio
@pytest.mark.parametrize("template_category_name", template_category_names())
def test_parse_content(data_env, template_category_name):
    """템플릿 파싱 테스트"""
    base_path = get_base_path()
    schema_path = base_path / "templates" / template_category_name / "schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    schema_data = generate_object(schema)

    success_count = 0
    for enum in TemplateItems:
        try:
            template_name = f"templates/{template_category_name}/{enum.value}"
            print(template_name)
            template = data_env.get_template(template_name)
            print(template.render(schema_data))
            success_count += 1
        except TemplateNotFound:
            pass

    assert success_count > 0


@pytest.mark.parametrize(
    "file_name,expected",
    [
        # 유효한 파일명
        ("test", True),
        ("test_123", True),
        ("test-partial", True),
        ("layout_test", True),
        ("template_1", True),
        ("a" * 255, True),  # 최대 길이
        # 빈 문자열
        ("", False),
        ("   ", False),
        # 숨김/시스템/임시 파일
        (".test", False),
        ("~test", False),
        ("..test", False),
        # 길이 초과
        ("a" * 256, False),
        # 허용되지 않는 문자
        ("test/test", False),
        ("test\\test", False),
        ("test:test", False),
        ("test*test", False),
        ("test?test", False),
        ('test"test', False),
        ("test<test", False),
        ("test>test", False),
        ("test|test", False),
        ("test test", False),  # 공백
        # 특수 케이스
        (".", False),
        ("..", False),
    ],
)
def test_check_file_name(temp_env: TemplyEnv, file_name: str, expected: bool):
    """파일명 검증 테스트

    Args:
        temp_env: TemplyEnv 인스턴스
        file_name: 테스트할 파일명
        expected: 예상되는 결과
    """
    assert temp_env.check_file_name(file_name) == expected


@pytest.mark.asyncio
async def test_temply_env_initialization(temp_env: TemplyEnv):
    """TemplyEnv 초기화 테스트"""
    assert temp_env.templates_dir.exists()
    assert temp_env.layouts_dir.exists()
    assert temp_env.partials_dir.exists()
    assert temp_env.file_encoding == "utf-8"


@pytest.mark.asyncio
async def test_temply_env_get_source(temp_env: TemplyEnv):
    """템플릿 소스 조회 테스트"""
    # 레이아웃 생성
    layout_path = temp_env.layouts_dir / "test_layout"
    layout_path.write_text("test layout content", encoding=temp_env.file_encoding)

    # 파셜 생성
    partial_path = temp_env.partials_dir / "test_partial"
    partial_path.write_text("test partial content", encoding=temp_env.file_encoding)

    # 템플릿 생성
    template_dir = temp_env.templates_dir / "test_category"
    template_dir.mkdir(exist_ok=True)
    template_path = template_dir / TemplateItems.HTML_EMAIL.value
    template_path.write_text("test template content", encoding=temp_env.file_encoding)

    # 소스 조회 테스트
    layout_source, _, _ = temp_env.get_source_layout("test_layout")
    assert "test layout content" in layout_source

    partial_source, _, _ = temp_env.get_source_partial("test_partial")
    assert "test partial content" in partial_source

    template_source, _, _ = temp_env.get_source_template(
        "test_category", TemplateItems.HTML_EMAIL.value
    )
    assert "test template content" in template_source


@pytest.mark.asyncio
async def test_temply_env_get_template(temp_env: TemplyEnv):
    """템플릿 조회 테스트"""
    # 템플릿 생성
    template_dir = temp_env.templates_dir / "test_category"
    template_dir.mkdir(exist_ok=True)
    template_path = template_dir / TemplateItems.HTML_EMAIL.value
    template_path.write_text("test template content", encoding=temp_env.file_encoding)

    # 템플릿 조회
    template = temp_env.get_template(f"templates/test_category/{TemplateItems.HTML_EMAIL.value}")
    assert template.render() == "test template content"


@pytest.mark.asyncio
async def test_temply_env_get_category_names(temp_env: TemplyEnv):
    """카테고리 목록 조회 테스트"""
    # 카테고리 생성
    categories = ["category1", "category2", "category3"]
    for category in categories:
        (temp_env.templates_dir / category).mkdir(exist_ok=True)

    # 카테고리 목록 조회
    category_names = temp_env.get_category_names()
    assert set(category_names) == set(categories)


@pytest.mark.asyncio
async def test_temply_env_get_template_names(temp_env: TemplyEnv):
    """템플릿 목록 조회 테스트"""
    # 카테고리와 템플릿 생성
    category = "test_category"
    category_dir = temp_env.templates_dir / category
    category_dir.mkdir(exist_ok=True)

    templates = [TemplateItems.HTML_EMAIL.value, TemplateItems.TEXT_EMAIL.value]
    for template in templates:
        (category_dir / template).write_text("test content", encoding=temp_env.file_encoding)

    # 템플릿 목록 조회
    template_names = temp_env.get_template_names(category)
    assert set(template_names) == set(templates)


@pytest.mark.asyncio
async def test_temply_env_check_file_name(temp_env: TemplyEnv):
    """파일명 검사 테스트"""
    # 유효한 파일명
    assert temp_env.check_file_name("valid_name")
    assert temp_env.check_file_name("valid-name")
    assert temp_env.check_file_name("valid_name_123")

    # 유효하지 않은 파일명
    assert not temp_env.check_file_name("")  # 빈 문자열
    assert not temp_env.check_file_name(" ")  # 공백만 있는 문자열
    assert not temp_env.check_file_name(".hidden")  # 숨김 파일
    assert not temp_env.check_file_name("invalid/name")  # 슬래시 포함
    assert not temp_env.check_file_name("invalid:name")  # 콜론 포함
    assert not temp_env.check_file_name("invalid*name")  # 별표 포함
    assert not temp_env.check_file_name("invalid?name")  # 물음표 포함
    assert not temp_env.check_file_name('invalid"name')  # 따옴표 포함
    assert not temp_env.check_file_name("invalid<name")  # 꺾쇠 포함
    assert not temp_env.check_file_name("invalid>name")  # 꺾쇠 포함
    assert not temp_env.check_file_name("invalid|name")  # 파이프 포함
    assert not temp_env.check_file_name("invalid name")  # 공백 포함


@pytest.mark.asyncio
async def test_temply_env_make_jinja_format(temp_env: TemplyEnv):
    """Jinja 포맷 생성 테스트"""
    # 메타 데이터 포맷

    meta = BaseMetaData(
        description="test description",
        created_at=BaseMetaData.get_current_datetime(),
        created_by="test",
        updated_at=BaseMetaData.get_current_datetime(),
        updated_by="test",
    )
    meta_format = temp_env.make_meta_jinja_format(meta)
    assert "test description" in meta_format
    assert "test" in meta_format

    # 레이아웃 포맷
    layout_format = temp_env.make_layout_jinja_format("test_layout")
    assert "{%- extends 'layouts/test_layout' -%}" in layout_format

    # 파셜 포맷
    partials = {"test_partial"}
    partials_format = temp_env.make_partials_jinja_format(partials)
    assert (
        "{%- from 'partials/test_partial' import render as partials_test_partial with context -%}"
        in partials_format
    )

    # 본문 포맷
    content = "test content"
    layout_body = temp_env.make_layout_body_jinja_format(content)
    assert "{%- block content -%}" in layout_body
    assert content in layout_body

    partial_body = temp_env.make_partial_body_jinja_format(content)
    assert "{%- macro render(locals = {}) -%}" in partial_body
    assert content in partial_body

    template_body = temp_env.make_template_body_jinja_format(content)
    assert "{%- block content -%}" in template_body
    assert content in template_body
