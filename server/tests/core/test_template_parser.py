"""템플릿 파서 테스트"""

import pytest

from app.core.temply.parser.template_parser import TemplateParser


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
