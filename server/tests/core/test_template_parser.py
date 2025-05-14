"""템플릿 파서 테스트"""

from pathlib import Path

import pytest
import pytest_asyncio

from app.core.temply.metadata.template_parser import TemplateParser


def get_base_path() -> Path:
    """테스트 데이터 경로"""
    base = Path(__file__).parent.parent / "data"
    return base


@pytest_asyncio.fixture
async def parser():
    """템플릿 파서 인스턴스를 생성하는 fixture"""
    base_path = get_base_path()
    _parser = TemplateParser(base_path / "templates")
    # pylint: disable=protected-access
    await _parser._ensure_initialized()  # 초기화 완료 대기
    yield _parser  # return 대신 yield 사용


@pytest.mark.asyncio
async def test_template_parser_with_layout(parser):
    """레이아웃이 있는 템플릿 파서 테스트"""
    templates = await parser.get_templates()
    assert any(template.layout for template in templates), "레이아웃이 있는 템플릿이 있어야 합니다"


@pytest.mark.asyncio
async def test_template_parser_with_partials(parser):
    """파셜이 있는 템플릿 파서 테스트"""
    templates = await parser.get_templates()
    assert any(template.partials for template in templates), "파셜이 있는 템플릿이 있어야 합니다"


async def get_test_parser(tmp_path):
    """Test parser instance for testing."""
    return TemplateParser(tmp_path)


@pytest.mark.asyncio
async def test_get_template_files(tmp_path):
    """Test getting list of template files with meta info."""
    # 테스트용 템플릿 파일 생성
    category_dir = tmp_path / "test_category"
    category_dir.mkdir()
    test_file = category_dir / "test_template.html"
    test_file.write_text(
        """{#-\ndescription: 템플릿 테스트\ncreated_at: 2024-07-01 00:00:00\n-#}\nContent"""
    )
    tmp_parser = await get_test_parser(tmp_path)
    templates = await tmp_parser.get_templates()
    assert len(templates) == 1
    assert templates[0].category == "test_category"
    assert templates[0].name == "test_template.html"
    assert templates[0].description == "템플릿 테스트"
    assert templates[0].created_at.strftime("%Y-%m-%d %H:%M:%S") == "2024-07-01 00:00:00"


@pytest.mark.asyncio
async def test_build_template_tree(parser):
    """Test building the template tree."""
    templates = await parser.get_templates()
    assert len(templates) > 0

    # Check that all nodes have the correct structure
    for node in templates:
        assert hasattr(node, "name")
        assert hasattr(node, "category")
        assert hasattr(node, "layout")
        assert hasattr(node, "partials")


@pytest.mark.asyncio
async def test_print_template_tree(parser, capsys):
    """Test printing the template tree."""
    await parser.print_template_tree()
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert "└─" in captured.out
    assert "layouts/" in captured.out
    assert "partials/" in captured.out
