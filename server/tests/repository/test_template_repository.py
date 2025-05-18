"""템플릿 리포지토리 테스트"""

import pytest

from app.core.exceptions import TemplateAlreadyExistsError, TemplateNotFoundError
from app.core.temply.temply_env import TemplateItems, TemplyEnv
from app.models.common_model import User
from app.models.layout_model import LayoutCreate
from app.models.partial_model import PartialCreate
from app.models.template_model import TemplateCreate, TemplateUpdate
from app.repositories.layout_repository import LayoutRepository
from app.repositories.partial_repository import PartialRepository
from app.repositories.template_repository import TemplateRepository


@pytest.mark.asyncio
async def test_template_repository(temp_env: TemplyEnv, user: User):
    """기본 템플릿 생성/조회 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)
    assert create_template.layout == create_layout.name
    assert create_template.partials == [create_partial.name]
    assert create_template.content == template_create.content
    assert create_template.description == template_create.description
    assert create_template.name == template_create.name
    assert create_template.category == template_create.category
    assert create_template.updated_at is not None
    assert create_template.updated_by == user.name
    assert create_template.created_at is not None
    assert create_template.created_by == user.name

    load_content, _, _ = temp_env.get_source_template(
        create_template.category, create_template.name
    )
    assert temp_env.make_layout_jinja_format(create_template.layout) in load_content
    assert (
        "\n".join(temp_env.make_partials_jinja_format(set(create_template.partials)))
        in load_content
    )
    assert create_template.content in load_content

    get_template = await template_repository.get(create_template.category, create_template.name)
    assert get_template.layout == create_template.layout
    assert get_template.partials == create_template.partials
    assert get_template.content == create_template.content
    assert get_template.description == create_template.description
    assert get_template.name == create_template.name


@pytest.mark.asyncio
async def test_template_duplicate(temp_env: TemplyEnv, user: User):
    """중복 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    await template_repository.create(user, template_create)
    with pytest.raises(TemplateAlreadyExistsError):
        await template_repository.create(user, template_create)


@pytest.mark.asyncio
async def test_template_not_found(temp_env: TemplyEnv):
    """존재하지 않는 템플릿 조회 테스트"""
    template_repository = TemplateRepository(temp_env)
    with pytest.raises(TemplateNotFoundError):
        await template_repository.get("non_existent_category", "non_existent_template")


@pytest.mark.asyncio
async def test_template_update(temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)

    # 업데이트
    update_content = "updated content"
    update_description = "updated description"
    update_template = await template_repository.update(
        user,
        create_template.category,
        create_template.name,
        TemplateUpdate(
            content=update_content,
            description=update_description,
            layout=create_layout.name,
            partials=[create_partial.name],
        ),
    )
    assert update_template.content == update_content
    assert update_template.description == update_description
    assert update_template.created_at == create_template.created_at
    assert update_template.created_by == create_template.created_by
    assert update_template.updated_at is not None
    assert update_template.updated_by == user.name


@pytest.mark.asyncio
async def test_template_invalid_name(temp_env: TemplyEnv, user: User):
    """잘못된 템플릿 이름 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    template_repository = TemplateRepository(temp_env)
    invalid_names = [
        "test/template",  # 슬래시 포함
        "test template",  # 공백 포함
        "test:template",  # 콜론 포함
        "test*template",  # 별표 포함
        "test?template",  # 물음표 포함
        'test"template',  # 따옴표 포함
        "test<template",  # 꺾쇠 포함
        "test>template",  # 꺾쇠 포함
        "test|template",  # 파이프 포함
    ]

    for invalid_name in invalid_names:
        with pytest.raises(ValueError):
            await template_repository.create(
                user,
                TemplateCreate(
                    category="test",
                    name=invalid_name,
                    description="test description",
                    layout=create_layout.name,
                    partials=[create_partial.name],
                    content="test content",
                ),
            )


@pytest.mark.asyncio
async def test_template_delete(temp_env: TemplyEnv, user: User):
    """템플릿 삭제 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)

    # 삭제
    await template_repository.delete(create_template.category, create_template.name)

    # 삭제 확인
    with pytest.raises(TemplateNotFoundError):
        await template_repository.get(create_template.category, create_template.name)


@pytest.mark.asyncio
async def test_template_with_multiple_partials(temp_env: TemplyEnv, user: User):
    """여러 파셜을 사용하는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    # 여러 파셜 생성
    partials = []
    for i in range(3):
        partial_create = PartialCreate(
            name=f"test_partial_{i}",
            content=f"test partial content {i}",
            description=f"test partial description {i}",
            dependencies=set(),
        )
        partials.append(await partial_repository.create(user, partial_create))

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[p.name for p in partials],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)

    # 생성된 템플릿 검증
    get_template = await template_repository.get(create_template.category, create_template.name)
    assert get_template.partials is not None
    assert len(get_template.partials) == len(partials)
    for partial in partials:
        assert partial.name in get_template.partials

    # 파일 내용 검증
    load_content, _, _ = temp_env.get_source_template(
        create_template.category, create_template.name
    )
    for partial in partials:
        assert (
            f"{{%- from 'partials/{partial.name}' import render as partials_{partial.name} with context -%}}"
            in load_content
        )


@pytest.mark.asyncio
async def test_template_with_nested_partials(temp_env: TemplyEnv, user: User):
    """중첩된 파셜을 사용하는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    # 기본 파셜 생성
    base_partial = await partial_repository.create(
        user,
        PartialCreate(
            name="base_partial",
            content="base content",
            description="base description",
            dependencies=set(),
        ),
    )

    # 기본 파셜을 의존하는 파셜 생성
    dependent_partial = await partial_repository.create(
        user,
        PartialCreate(
            name="dependent_partial",
            content="dependent content",
            description="dependent description",
            dependencies={base_partial.name},
        ),
    )

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[base_partial.name, dependent_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)

    # 생성된 템플릿 검증
    get_template = await template_repository.get(create_template.category, create_template.name)
    assert get_template.partials is not None
    assert base_partial.name in get_template.partials
    assert dependent_partial.name in get_template.partials

    # 파일 내용 검증
    load_content, _, _ = temp_env.get_source_template(
        create_template.category, create_template.name
    )
    assert (
        f"{{%- from 'partials/{base_partial.name}' import render as partials_{base_partial.name} with context -%}}"
        in load_content
    )
    assert (
        f"{{%- from 'partials/{dependent_partial.name}' import render as partials_{dependent_partial.name} with context -%}}"
        in load_content
    )


@pytest.mark.asyncio
async def test_template_without_layout_and_partials(temp_env: TemplyEnv, user: User):
    """레이아웃과 파셜이 없는 템플릿 생성 테스트"""
    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=None,
        partials=[],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)
    assert create_template.layout == ""  # None 대신 빈 문자열로 처리
    assert create_template.partials == []
    assert create_template.content == template_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.get_source_template(
        create_template.category, create_template.name
    )
    assert "{%- extends" not in load_content
    assert "{%- from 'partials/" not in load_content
    assert create_template.content in load_content


@pytest.mark.asyncio
async def test_template_without_layout(temp_env: TemplyEnv, user: User):
    """레이아웃이 없는 템플릿 생성 테스트"""
    partial_repository = PartialRepository(temp_env)
    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=None,
        partials=[create_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)
    assert create_template.layout == ""  # None 대신 빈 문자열로 처리
    assert create_template.partials == [create_partial.name]
    assert create_template.content == template_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.get_source_template(
        create_template.category, create_template.name
    )
    assert "{%- extends" not in load_content
    assert (
        f"{{%- from 'partials/{create_partial.name}' import render as partials_{create_partial.name} with context -%}}"
        in load_content
    )
    assert create_template.content in load_content


@pytest.mark.asyncio
async def test_template_without_partials(temp_env: TemplyEnv, user: User):
    """파셜이 없는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)
    assert create_template.layout == create_layout.name
    assert create_template.partials == []
    assert create_template.content == template_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.get_source_template(
        create_template.category, create_template.name
    )
    assert temp_env.make_layout_jinja_format(create_template.layout) in load_content
    assert "{%- from 'partials/" not in load_content
    assert create_template.content in load_content


@pytest.mark.asyncio
async def test_template_with_single_partial(temp_env: TemplyEnv, user: User):
    """단일 파셜을 사용하는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)
    assert create_template.layout == create_layout.name
    assert create_template.partials == [create_partial.name]
    assert create_template.content == template_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.get_source_template(
        create_template.category, create_template.name
    )
    assert temp_env.make_layout_jinja_format(create_template.layout) in load_content
    assert (
        f"{{%- from 'partials/{create_partial.name}' import render as partials_{create_partial.name} with context -%}}"
        in load_content
    )
    assert create_template.content in load_content


@pytest.mark.asyncio
async def test_template_with_two_partials(temp_env: TemplyEnv, user: User):
    """두 개의 파셜을 사용하는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    # 두 개의 파셜 생성
    partials = []
    for i in range(2):
        partial_create = PartialCreate(
            name=f"test_partial_{i}",
            content=f"test partial content {i}",
            description=f"test partial description {i}",
            dependencies=set(),
        )
        partials.append(await partial_repository.create(user, partial_create))

    template_repository = TemplateRepository(temp_env)
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[p.name for p in partials],
        content="test content",
    )
    create_template = await template_repository.create(user, template_create)
    assert create_template.layout == create_layout.name
    assert create_template.partials is not None
    assert len(create_template.partials) == 2
    for partial in partials:
        assert partial.name in create_template.partials
    assert create_template.content == template_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.get_source_template(
        create_template.category, create_template.name
    )
    assert temp_env.make_layout_jinja_format(create_template.layout) in load_content
    for partial in partials:
        assert (
            f"{{%- from 'partials/{partial.name}' import render as partials_{partial.name} with context -%}}"
            in load_content
        )
    assert create_template.content in load_content
