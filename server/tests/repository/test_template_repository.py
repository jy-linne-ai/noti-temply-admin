"""템플릿 리포지토리 테스트"""

import pytest

from app.core.exceptions import (
    LayoutNotFoundError,
    PartialNotFoundError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
)
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
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    category = "test"
    create_template = await template_repository.create(user, category, template_create)
    assert create_template.layout == create_layout.name
    assert create_template.partials == [create_partial.name]
    assert create_template.content == template_create.content
    assert create_template.description == template_create.description
    assert create_template.name == template_create.name
    assert create_template.category == category
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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    await template_repository.create(user, category, template_create)
    with pytest.raises(TemplateAlreadyExistsError):
        await template_repository.create(user, category, template_create)


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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, category, template_create)

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
            category = "test"
            await template_repository.create(
                user,
                category,
                TemplateCreate(
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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, category, template_create)

    # 삭제
    await template_repository.delete(user, create_template.category, create_template.name)

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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[p.name for p in partials],
        content="test content",
    )
    create_template = await template_repository.create(user, category, template_create)

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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[base_partial.name, dependent_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, category, template_create)

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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=None,
        partials=[],
        content="test content",
    )
    create_template = await template_repository.create(user, category, template_create)
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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=None,
        partials=[create_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, category, template_create)
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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[],
        content="test content",
    )
    create_template = await template_repository.create(user, category, template_create)
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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_template = await template_repository.create(user, category, template_create)
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
    category = "test"
    template_create = TemplateCreate(
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[p.name for p in partials],
        content="test content",
    )
    create_template = await template_repository.create(user, category, template_create)
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


@pytest.mark.asyncio
async def test_template_update_layout(temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 시 레이아웃 변경 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)

    # 기존 레이아웃 생성
    old_layout = await layout_repository.create(
        user,
        LayoutCreate(
            name="old_layout",
            content="old layout content",
            description="old layout description",
        ),
    )

    # 새 레이아웃 생성
    new_layout = await layout_repository.create(
        user,
        LayoutCreate(
            name="new_layout",
            content="new layout content",
            description="new layout description",
        ),
    )

    # 파셜 생성
    partial = await partial_repository.create(
        user,
        PartialCreate(
            name="test_partial",
            content="test partial content",
            description="test partial description",
            dependencies=set(),
        ),
    )

    # 템플릿 생성
    template_repository = TemplateRepository(temp_env)
    category = "test"
    template = await template_repository.create(
        user,
        category,
        TemplateCreate(
            name=TemplateItems.HTML_EMAIL.value,
            description="test description",
            layout=old_layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 레이아웃 변경
    updated_template = await template_repository.update(
        user,
        template.category,
        template.name,
        TemplateUpdate(
            content=template.content,
            description=template.description,
            layout=new_layout.name,
            partials=template.partials,
        ),
    )

    assert updated_template.layout == new_layout.name
    assert updated_template.content == template.content
    assert updated_template.partials == template.partials

    # 파일 내용 검증
    load_content, _, _ = temp_env.get_source_template(
        updated_template.category, updated_template.name
    )
    assert temp_env.make_layout_jinja_format(new_layout.name) in load_content


@pytest.mark.asyncio
async def test_template_update_partials(temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 시 파셜 변경 테스트"""
    layout_repository = LayoutRepository(temp_env)
    partial_repository = PartialRepository(temp_env)

    # 레이아웃 생성
    layout = await layout_repository.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    # 기존 파셜들 생성
    old_partials = []
    for i in range(2):
        partial = await partial_repository.create(
            user,
            PartialCreate(
                name=f"old_partial_{i}",
                content=f"old partial content {i}",
                description=f"old partial description {i}",
                dependencies=set(),
            ),
        )
        old_partials.append(partial)

    # 새 파셜들 생성
    new_partials = []
    for i in range(2):
        partial = await partial_repository.create(
            user,
            PartialCreate(
                name=f"new_partial_{i}",
                content=f"new partial content {i}",
                description=f"new partial description {i}",
                dependencies=set(),
            ),
        )
        new_partials.append(partial)

    # 템플릿 생성
    template_repository = TemplateRepository(temp_env)
    category = "test"
    template = await template_repository.create(
        user,
        category,
        TemplateCreate(
            name=TemplateItems.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[p.name for p in old_partials],
            content="test content",
        ),
    )

    # 파셜 변경
    updated_template = await template_repository.update(
        user,
        template.category,
        template.name,
        TemplateUpdate(
            content=template.content,
            description=template.description,
            layout=layout.name,
            partials=[p.name for p in new_partials],
        ),
    )

    assert updated_template.layout == layout.name
    assert updated_template.content == template.content
    assert set(updated_template.partials or []) == {p.name for p in new_partials}

    # 파일 내용 검증
    load_content, _, _ = temp_env.get_source_template(
        updated_template.category, updated_template.name
    )
    for partial in new_partials:
        assert (
            f"{{%- from 'partials/{partial.name}' import render as partials_{partial.name} with context -%}}"
            in load_content
        )


@pytest.mark.asyncio
async def test_template_nonexistent_layout(temp_env: TemplyEnv, user: User):
    """존재하지 않는 레이아웃 참조 테스트"""
    partial_repository = PartialRepository(temp_env)
    partial = await partial_repository.create(
        user,
        PartialCreate(
            name="test_partial",
            content="test partial content",
            description="test partial description",
            dependencies=set(),
        ),
    )

    template_repository = TemplateRepository(temp_env)
    with pytest.raises(LayoutNotFoundError):
        category = "test"
        await template_repository.create(
            user,
            category,
            TemplateCreate(
                name=TemplateItems.HTML_EMAIL.value,
                description="test description",
                layout="nonexistent_layout",
                partials=[partial.name],
                content="test content",
            ),
        )


@pytest.mark.asyncio
async def test_template_nonexistent_partial(temp_env: TemplyEnv, user: User):
    """존재하지 않는 파셜 참조 테스트"""
    layout_repository = LayoutRepository(temp_env)
    layout = await layout_repository.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    template_repository = TemplateRepository(temp_env)
    with pytest.raises(PartialNotFoundError):
        category = "test"
        await template_repository.create(
            user,
            category,
            TemplateCreate(
                name=TemplateItems.HTML_EMAIL.value,
                description="test description",
                layout=layout.name,
                partials=["nonexistent_partial"],
                content="test content",
            ),
        )


@pytest.mark.asyncio
async def test_template_repository_get_categories(temp_env: TemplyEnv, user: User):
    """카테고리 목록 조회 테스트"""

    template_repository = TemplateRepository(temp_env)
    category = "test_category"
    template_name = TemplateItems.HTML_EMAIL.value
    template_create = TemplateCreate(
        name=template_name,
        content="test content",
        description="test description",
        layout=None,
        partials=None,
    )

    # 템플릿 생성
    await template_repository.create(user, category, template_create)

    # 카테고리 목록 조회
    categories = await template_repository.get_categories()
    assert category in categories


@pytest.mark.asyncio
async def test_template_repository_get_templates_by_category(temp_env: TemplyEnv, user: User):
    """카테고리별 템플릿 목록 조회 테스트"""

    template_repository = TemplateRepository(temp_env)
    category = "test_category"
    template_name = TemplateItems.HTML_EMAIL.value
    template_create = TemplateCreate(
        name=template_name,
        content="test content",
        description="test description",
        layout=None,
        partials=None,
    )

    # 템플릿 생성
    await template_repository.create(user, category, template_create)

    # 카테고리별 템플릿 목록 조회
    templates = await template_repository.get_templates(category)
    assert len(templates) == 1
    assert templates[0].name == template_name
    assert templates[0].category == category


@pytest.mark.asyncio
async def test_template_repository_delete_templates_by_category(temp_env: TemplyEnv, user: User):
    """카테고리별 템플릿 삭제 테스트"""

    template_repository = TemplateRepository(temp_env)
    category = "test_category"
    template_name = TemplateItems.HTML_EMAIL.value
    template_create = TemplateCreate(
        name=template_name,
        content="test content",
        description="test description",
        layout=None,
        partials=None,
    )

    # 템플릿 생성
    await template_repository.create(user, category, template_create)

    # 카테고리별 템플릿 삭제
    await template_repository.delete_templates(user, category)

    # 템플릿이 삭제되었는지 확인
    with pytest.raises(TemplateNotFoundError):
        await template_repository.get(category, template_name)

    # 카테고리별 템플릿 목록이 비어있는지 확인
    templates = await template_repository.get_templates(category)
    assert len(templates) == 0
