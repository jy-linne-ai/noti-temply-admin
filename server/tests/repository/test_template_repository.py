"""템플릿 리포지토리 테스트"""

import pytest

from app.core.exceptions import (
    LayoutNotFoundError,
    PartialNotFoundError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
)
from app.core.temply.temply_env import TemplateComponents, TemplyEnv
from app.models.common_model import User, VersionInfo
from app.models.layout_model import LayoutCreate
from app.models.partial_model import PartialCreate
from app.models.template_model import TemplateComponentCreate, TemplateComponentUpdate
from app.repositories.layout_repository import LayoutRepository
from app.repositories.partial_repository import PartialRepository
from app.repositories.template_repository import TemplateRepository


@pytest.mark.asyncio
async def test_template_repository(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """기본 템플릿 생성/조회 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)
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

    template_repository = TemplateRepository(version_info, temp_env)
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    template = "test"
    create_component = await template_repository.create_component(user, template, component_create)
    assert create_component.layout == create_layout.name
    assert create_component.partials == [create_partial.name]
    assert create_component.content == component_create.content
    assert create_component.description == component_create.description
    assert create_component.template == template
    assert create_component.component == component_create.component
    assert create_component.updated_at is not None
    assert create_component.updated_by == user.name
    assert create_component.created_at is not None
    assert create_component.created_by == user.name

    load_content, _, _ = temp_env.load_component_source(
        create_component.template, create_component.component
    )
    assert temp_env.format_layout_block(create_component.layout) in load_content
    assert (
        "\n".join(temp_env.format_partial_imports(set(create_component.partials))) in load_content
    )
    assert create_component.content in load_content

    get_component = await template_repository.get_component(
        create_component.template, create_component.component
    )
    assert get_component.layout == create_component.layout
    assert get_component.partials == create_component.partials
    assert get_component.content == create_component.content
    assert get_component.description == create_component.description
    assert get_component.template == create_component.template


@pytest.mark.asyncio
async def test_template_duplicate(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """중복 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)
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

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    await template_repository.create_component(user, template, component_create)
    with pytest.raises(TemplateAlreadyExistsError):
        await template_repository.create_component(user, template, component_create)


@pytest.mark.asyncio
async def test_template_not_found(version_info: VersionInfo, temp_env: TemplyEnv):
    """존재하지 않는 템플릿 조회 테스트"""
    template_repository = TemplateRepository(version_info, temp_env)
    with pytest.raises(TemplateNotFoundError):
        await template_repository.get_component("non_existent_template", "non_existent_component")


@pytest.mark.asyncio
async def test_template_update(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)
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

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_component = await template_repository.create_component(user, template, component_create)

    # 업데이트
    update_content = "updated content"
    update_description = "updated description"
    update_component = await template_repository.update_component(
        user,
        create_component.template,
        create_component.component,
        TemplateComponentUpdate(
            content=update_content,
            description=update_description,
            layout=create_layout.name,
            partials=[create_partial.name],
        ),
    )
    assert update_component.content == update_content
    assert update_component.description == update_description
    assert update_component.created_at == create_component.created_at
    assert update_component.created_by == create_component.created_by
    assert update_component.updated_at is not None
    assert update_component.updated_by == user.name


@pytest.mark.asyncio
async def test_template_invalid_name(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """잘못된 템플릿 이름 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)
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

    template_repository = TemplateRepository(version_info, temp_env)
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
            template = "test"
            await template_repository.create_component(
                user,
                template,
                TemplateComponentCreate(
                    component=invalid_name,
                    description="test description",
                    layout=create_layout.name,
                    partials=[create_partial.name],
                    content="test content",
                ),
            )


@pytest.mark.asyncio
async def test_template_delete(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """템플릿 삭제 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)
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

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_component = await template_repository.create_component(user, template, component_create)

    # 삭제
    await template_repository.delete_component(
        user, create_component.template, create_component.component
    )

    # 삭제 확인
    with pytest.raises(TemplateNotFoundError):
        await template_repository.get_component(
            create_component.template, create_component.component
        )


@pytest.mark.asyncio
async def test_template_with_multiple_partials(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """여러 파셜을 사용하는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)
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

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[p.name for p in partials],
        content="test content",
    )
    create_component = await template_repository.create_component(user, template, component_create)

    # 생성된 템플릿 검증
    get_component = await template_repository.get_component(
        create_component.template, create_component.component
    )
    assert get_component.partials is not None
    assert len(get_component.partials) == len(partials)
    for partial in partials:
        assert partial.name in get_component.partials

    # 파일 내용 검증
    load_content, _, _ = temp_env.load_component_source(
        create_component.template, create_component.component
    )
    for partial in partials:
        assert (
            f"{{%- from 'partials/{partial.name}' import render as {temp_env._get_import_name(partial.name)} with context -%}}"
            in load_content
        )


@pytest.mark.asyncio
async def test_template_with_nested_partials(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """중첩된 파셜을 사용하는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)
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

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[base_partial.name, dependent_partial.name],
        content="test content",
    )
    create_component = await template_repository.create_component(user, template, component_create)

    # 생성된 템플릿 검증
    get_component = await template_repository.get_component(
        create_component.template, create_component.component
    )
    assert get_component.partials is not None
    assert base_partial.name in get_component.partials
    assert dependent_partial.name in get_component.partials

    # 파일 내용 검증
    load_content, _, _ = temp_env.load_component_source(
        create_component.template, create_component.component
    )
    assert (
        f"{{%- from 'partials/{base_partial.name}' import render as {temp_env._get_import_name(base_partial.name)} with context -%}}"
        in load_content
    )
    assert (
        f"{{%- from 'partials/{dependent_partial.name}' import render as {temp_env._get_import_name(dependent_partial.name)} with context -%}}"
        in load_content
    )


@pytest.mark.asyncio
async def test_template_without_layout_and_partials(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """레이아웃과 파셜이 없는 템플릿 생성 테스트"""
    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=None,
        partials=[],
        content="test content",
    )
    create_component = await template_repository.create_component(user, template, component_create)
    assert create_component.layout == ""  # None 대신 빈 문자열로 처리
    assert create_component.partials == []
    assert create_component.content == component_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.load_component_source(
        create_component.template, create_component.component
    )
    assert "{%- extends" not in load_content
    assert "{%- from 'partials/" not in load_content
    assert create_component.content in load_content


@pytest.mark.asyncio
async def test_template_without_layout(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """레이아웃이 없는 템플릿 생성 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)
    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=None,
        partials=[create_partial.name],
        content="test content",
    )
    create_component = await template_repository.create_component(user, template, component_create)
    assert create_component.layout == ""  # None 대신 빈 문자열로 처리
    assert create_component.partials == [create_partial.name]
    assert create_component.content == component_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.load_component_source(
        create_component.template, create_component.component
    )
    assert "{%- extends" not in load_content
    assert (
        f"{{%- from 'partials/{create_partial.name}' import render as {temp_env._get_import_name(create_partial.name)} with context -%}}"
        in load_content
    )
    assert create_component.content in load_content


@pytest.mark.asyncio
async def test_template_without_partials(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """파셜이 없는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[],
        content="test content",
    )
    create_component = await template_repository.create_component(user, template, component_create)
    assert create_component.layout == create_layout.name
    assert create_component.partials == []
    assert create_component.content == component_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.load_component_source(
        create_component.template, create_component.component
    )
    assert temp_env.format_layout_block(create_component.layout) in load_content
    assert "{%- from 'partials/" not in load_content
    assert create_component.content in load_content


@pytest.mark.asyncio
async def test_template_with_single_partial(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """단일 파셜을 사용하는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    layout_create = LayoutCreate(
        name="layout_test",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    partial_repository = PartialRepository(version_info, temp_env)
    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[create_partial.name],
        content="test content",
    )
    create_component = await template_repository.create_component(user, template, component_create)
    assert create_component.layout == create_layout.name
    assert create_component.partials == [create_partial.name]
    assert create_component.content == component_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.load_component_source(
        create_component.template, create_component.component
    )
    assert temp_env.format_layout_block(create_component.layout) in load_content
    assert (
        f"{{%- from 'partials/{create_partial.name}' import render as {temp_env._get_import_name(create_partial.name)} with context -%}}"
        in load_content
    )
    assert create_component.content in load_content


@pytest.mark.asyncio
async def test_template_with_two_partials(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """두 개의 파셜을 사용하는 템플릿 생성 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)
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

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    component_create = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=create_layout.name,
        partials=[p.name for p in partials],
        content="test content",
    )
    create_component = await template_repository.create_component(user, template, component_create)
    assert create_component.layout == create_layout.name
    assert create_component.partials is not None
    assert len(create_component.partials) == 2
    for partial in partials:
        assert partial.name in create_component.partials
    assert create_component.content == component_create.content

    # 파일 내용 검증
    load_content, _, _ = temp_env.load_component_source(
        create_component.template, create_component.component
    )
    assert temp_env.format_layout_block(create_component.layout) in load_content
    for partial in partials:
        assert (
            f"{{%- from 'partials/{partial.name}' import render as {temp_env._get_import_name(partial.name)} with context -%}}"
            in load_content
        )
    assert create_component.content in load_content


@pytest.mark.asyncio
async def test_template_update_layout(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 시 레이아웃 변경 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)

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
    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    created_component = await template_repository.create_component(
        user,
        template,
        TemplateComponentCreate(
            component=TemplateComponents.HTML_EMAIL.value,
            description="test description",
            layout=old_layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 레이아웃 변경
    updated_component = await template_repository.update_component(
        user,
        template,
        created_component.component,
        TemplateComponentUpdate(
            content=created_component.content,
            description=created_component.description,
            layout=new_layout.name,
            partials=created_component.partials,
        ),
    )

    assert updated_component.layout == new_layout.name
    assert updated_component.content == created_component.content
    assert updated_component.partials == created_component.partials

    # 파일 내용 검증
    load_content, _, _ = temp_env.load_component_source(
        updated_component.template, updated_component.component
    )
    assert temp_env.format_layout_block(new_layout.name) in load_content


@pytest.mark.asyncio
async def test_template_update_partials(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 시 파셜 변경 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    partial_repository = PartialRepository(version_info, temp_env)

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
    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    created_component = await template_repository.create_component(
        user,
        template,
        TemplateComponentCreate(
            component=TemplateComponents.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[p.name for p in old_partials],
            content="test content",
        ),
    )

    # 파셜 변경
    updated_component = await template_repository.update_component(
        user,
        template,
        created_component.component,
        TemplateComponentUpdate(
            content=created_component.content,
            description=created_component.description,
            layout=layout.name,
            partials=[p.name for p in new_partials],
        ),
    )

    assert updated_component.layout == layout.name
    assert updated_component.content == created_component.content
    assert set(updated_component.partials or []) == {p.name for p in new_partials}

    # 파일 내용 검증
    load_content, _, _ = temp_env.load_component_source(
        updated_component.template, updated_component.component
    )
    for partial in new_partials:
        assert (
            f"{{%- from 'partials/{partial.name}' import render as {temp_env._get_import_name(partial.name)} with context -%}}"
            in load_content
        )


@pytest.mark.asyncio
async def test_template_nonexistent_layout(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """존재하지 않는 레이아웃 참조 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)
    partial = await partial_repository.create(
        user,
        PartialCreate(
            name="test_partial",
            content="test partial content",
            description="test partial description",
            dependencies=set(),
        ),
    )

    template_repository = TemplateRepository(version_info, temp_env)
    with pytest.raises(LayoutNotFoundError):
        template = "test"
        await template_repository.create_component(
            user,
            template,
            TemplateComponentCreate(
                component=TemplateComponents.HTML_EMAIL.value,
                description="test description",
                layout="nonexistent_layout",
                partials=[partial.name],
                content="test content",
            ),
        )


@pytest.mark.asyncio
async def test_template_nonexistent_partial(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """존재하지 않는 파셜 참조 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    layout = await layout_repository.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    template_repository = TemplateRepository(version_info, temp_env)
    with pytest.raises(PartialNotFoundError):
        template = "test"
        await template_repository.create_component(
            user,
            template,
            TemplateComponentCreate(
                component=TemplateComponents.HTML_EMAIL.value,
                description="test description",
                layout=layout.name,
                partials=["nonexistent_partial"],
                content="test content",
            ),
        )


@pytest.mark.asyncio
async def test_template_repository_get_templates(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """템플릿 목록 조회 테스트"""

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    template_name = TemplateComponents.HTML_EMAIL.value
    component_create = TemplateComponentCreate(
        component=template_name,
        content="test content",
        description="test description",
        layout=None,
        partials=None,
    )

    # 템플릿 생성
    await template_repository.create_component(user, template, component_create)

    # 템플릿 목록 조회
    templates = await template_repository.get_template_names()
    assert template in templates


@pytest.mark.asyncio
async def test_template_repository_get_components_by_template(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """템플릿 목록 조회 테스트"""

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    template_name = TemplateComponents.HTML_EMAIL.value
    component_create = TemplateComponentCreate(
        component=template_name,
        content="test content",
        description="test description",
        layout=None,
        partials=None,
    )

    # 템플릿 생성
    await template_repository.create_component(user, template, component_create)

    # 템플릿별 템플릿 목록 조회
    components = await template_repository.get_components_by_template(template)
    assert len(components) == 1
    assert components[0].component == template_name
    assert components[0].template == template


@pytest.mark.asyncio
async def test_template_repository_delete_component_by_template(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """템플릿별 템플릿 삭제 테스트"""

    template_repository = TemplateRepository(version_info, temp_env)
    template = "test"
    template_name = TemplateComponents.HTML_EMAIL.value
    component_create = TemplateComponentCreate(
        component=template_name,
        content="test content",
        description="test description",
        layout=None,
        partials=None,
    )

    # 템플릿 생성
    await template_repository.create_component(user, template, component_create)

    # 템플릿별 템플릿 삭제
    await template_repository.delete_component(user, template, template_name)

    # 템플릿이 삭제되었는지 확인
    with pytest.raises(TemplateNotFoundError):
        await template_repository.get_component(template, template_name)

    # 템플릿별 템플릿 목록이 비어있는지 확인
    components = await template_repository.get_components_by_template(template)
    assert len(components) == 0
