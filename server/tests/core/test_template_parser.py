"""템플릿 파서 테스트"""

import pytest

from temply_app.core.exceptions import (
    LayoutNotFoundError,
    PartialNotFoundError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
)
from temply_app.core.temply.parser.template_parser import TemplateParser
from temply_app.core.temply.temply_env import TemplateComponents, TemplyEnv
from temply_app.models.common_model import User


@pytest.mark.asyncio
async def test_template_parser_with_layout(data_env):
    """레이아웃이 있는 템플릿 파서 테스트"""
    parser = TemplateParser(data_env)
    components = await parser.get_components()
    assert any(
        component.layout for component in components
    ), "레이아웃이 있는 템플릿이 있어야 합니다"


@pytest.mark.asyncio
async def test_template_parser_with_partials(data_env):
    """파셜이 있는 템플릿 파서 테스트"""
    parser = TemplateParser(data_env)
    components = await parser.get_components()
    assert any(component.partials for component in components), "파셜이 있는 템플릿이 있어야 합니다"


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
    components = await parser.get_components()
    assert len(components) == 1
    assert components[0].template == "test_category"
    assert components[0].component == "test_template.html"
    assert components[0].description == "템플릿 테스트"
    assert components[0].created_at.strftime("%Y-%m-%d %H:%M:%S") == "2024-07-01 00:00:00"


@pytest.mark.asyncio
async def test_build_template_tree(data_env):
    """Test building the template tree."""
    parser = TemplateParser(data_env)
    components = await parser.get_components()
    assert len(components) > 0

    # Check that all nodes have the correct structure
    for node in components:
        assert hasattr(node, "template")
        assert hasattr(node, "component")
        assert hasattr(node, "layout")
        assert hasattr(node, "partials")


@pytest.mark.asyncio
async def test_print_template_tree(data_env, capsys):
    """Test printing the template tree."""
    parser = TemplateParser(data_env)
    await parser.print_component_tree()
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert "└─" in captured.out
    assert "layouts/" in captured.out
    assert "partials/" in captured.out


@pytest.mark.asyncio
async def test_template_parser_get_template_components(temp_env: TemplyEnv, user: User):
    """템플릿 컴포넌트 목록 조회 테스트"""
    parser = TemplateParser(temp_env)
    template = "test_category"
    component_name = TemplateComponents.HTML_EMAIL.value
    content = "test content"
    description = "test description"
    layout = None
    partials = None

    # 템플릿 생성
    await parser.create_component(
        user,
        template,
        component_name,
        content,
        description,
        layout,
        partials,
    )

    # 템플릿 컴포넌트 목록 조회
    components = await parser.get_components_by_template(template)
    assert len(components) == 1
    assert components[0].template == template
    assert components[0].component == component_name
    assert components[0].description == description


@pytest.mark.asyncio
async def test_template_parser_get_template_components_by_template(temp_env: TemplyEnv, user: User):
    """템플릿별 템플릿 컴포넌트 목록 조회 테스트"""
    parser = TemplateParser(temp_env)
    template = "test_category"
    component_name = TemplateComponents.HTML_EMAIL.value
    content = "test content"
    description = "test description"
    layout = None
    partials = None

    # 템플릿 생성
    await parser.create_component(
        user,
        template,
        component_name,
        content,
        description,
        layout,
        partials,
    )

    # 템플릿별 템플릿 컴포넌트 목록 조회
    components = await parser.get_components_by_template(template)
    assert len(components) == 1
    assert components[0].template == template
    assert components[0].component == component_name


@pytest.mark.asyncio
async def test_template_parser_delete_template_components_by_template(
    temp_env: TemplyEnv, user: User
):
    """템플릿별 템플릿 컴포넌트 삭제 테스트"""
    parser = TemplateParser(temp_env)
    template = "test_category"
    component_name = TemplateComponents.HTML_EMAIL.value
    content = "test content"
    description = "test description"
    layout = None
    partials = None

    # 템플릿 생성
    await parser.create_component(
        user,
        template,
        component_name,
        content,
        description,
        layout,
        partials,
    )

    # 템플릿별 템플릿 컴포넌트 삭제
    await parser.delete_component(user, template, component_name)

    # 템플릿이 삭제되었는지 확인
    with pytest.raises(TemplateNotFoundError):
        await parser.get_component(template, component_name)

    # 템플릿별 템플릿 컴포넌트 목록이 비어있는지 확인
    components = await parser.get_components_by_template(template)
    assert len(components) == 0
