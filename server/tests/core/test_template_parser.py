"""템플릿 파서 테스트"""

import pytest

from app.core.exceptions import (
    LayoutNotFoundError,
    PartialNotFoundError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
)
from app.core.temply.parser.template_parser import TemplateParser
from app.core.temply.temply_env import TemplateItems, TemplyEnv
from app.models.common_model import User


@pytest.mark.asyncio
async def test_template_parser_with_layout(data_env):
    """레이아웃이 있는 템플릿 파서 테스트"""
    parser = TemplateParser(data_env)
    templates = await parser.get_templates()
    assert any(template.layout for template in templates), "레이아웃이 있는 템플릿이 있어야 합니다"


@pytest.mark.asyncio
async def test_template_parser_with_partials(data_env):
    """파셜이 있는 템플릿 파서 테스트"""
    parser = TemplateParser(data_env)
    templates = await parser.get_templates()
    assert any(template.partials for template in templates), "파셜이 있는 템플릿이 있어야 합니다"


@pytest.mark.asyncio
async def test_get_template_files(temp_env):
    """Test getting list of template files with meta info."""
    # 테스트용 템플릿 파일 생성
    category_dir = temp_env.templates_dir / "test_category"
    category_dir.mkdir(parents=True, exist_ok=True)
    test_file = category_dir / "test_template.html"
    test_file.write_text(
        """{#-\ndescription: 템플릿 테스트\ncreated_at: 2024-07-01 00:00:00\n-#}\nContent"""
    )
    parser = TemplateParser(temp_env)
    templates = await parser.get_templates()
    assert len(templates) == 1
    assert templates[0].category == "test_category"
    assert templates[0].name == "test_template.html"
    assert templates[0].description == "템플릿 테스트"
    assert templates[0].created_at.strftime("%Y-%m-%d %H:%M:%S") == "2024-07-01 00:00:00"


@pytest.mark.asyncio
async def test_build_template_tree(data_env):
    """Test building the template tree."""
    parser = TemplateParser(data_env)
    templates = await parser.get_templates()
    assert len(templates) > 0

    # Check that all nodes have the correct structure
    for node in templates:
        assert hasattr(node, "name")
        assert hasattr(node, "category")
        assert hasattr(node, "layout")
        assert hasattr(node, "partials")


@pytest.mark.asyncio
async def test_print_template_tree(data_env, capsys):
    """Test printing the template tree."""
    parser = TemplateParser(data_env)
    await parser.print_template_tree()
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert "└─" in captured.out
    assert "layouts/" in captured.out
    assert "partials/" in captured.out


@pytest.mark.asyncio
async def test_template_parser_get_categories(temp_env: TemplyEnv, user: User):
    """카테고리 목록 조회 테스트"""
    template_parser = TemplateParser(temp_env)
    category = "test_category"
    template_name = TemplateItems.HTML_EMAIL.value
    content = "test content"
    description = "test description"
    layout = None
    partials = None

    # 템플릿 생성
    await template_parser.create(
        user,
        category,
        template_name,
        content,
        description,
        layout,
        partials,
    )

    # 카테고리 목록 조회
    categories = await template_parser.get_categories()
    assert category in categories


@pytest.mark.asyncio
async def test_template_parser_get_templates_by_category(temp_env: TemplyEnv, user: User):
    """카테고리별 템플릿 목록 조회 테스트"""
    template_parser = TemplateParser(temp_env)
    category = "test_category"
    template_name = TemplateItems.HTML_EMAIL.value
    content = "test content"
    description = "test description"
    layout = None
    partials = None

    # 템플릿 생성
    await template_parser.create(
        user,
        category,
        template_name,
        content,
        description,
        layout,
        partials,
    )

    # 카테고리별 템플릿 목록 조회
    templates = await template_parser.get_templates_by_category(category)
    assert len(templates) == 1
    assert templates[0].name == template_name
    assert templates[0].category == category


@pytest.mark.asyncio
async def test_template_parser_delete_templates_by_category(temp_env: TemplyEnv, user: User):
    """카테고리별 템플릿 삭제 테스트"""
    template_parser = TemplateParser(temp_env)
    category = "test_category"
    template_name = TemplateItems.HTML_EMAIL.value
    content = "test content"
    description = "test description"
    layout = None
    partials = None

    # 템플릿 생성
    await template_parser.create(
        user,
        category,
        template_name,
        content,
        description,
        layout,
        partials,
    )

    # 카테고리별 템플릿 삭제
    await template_parser.delete_templates(user, category)

    # 템플릿이 삭제되었는지 확인
    with pytest.raises(TemplateNotFoundError):
        await template_parser.get_template(f"{category}/{template_name}")

    # 카테고리별 템플릿 목록이 비어있는지 확인
    templates = await template_parser.get_templates_by_category(category)
    assert len(templates) == 0
