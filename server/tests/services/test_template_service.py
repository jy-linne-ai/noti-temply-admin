"""템플릿 서비스 테스트"""

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
from app.services.layout_service import LayoutService
from app.services.partial_service import PartialService
from app.services.template_service import TemplateService


@pytest.mark.asyncio
async def test_template_service_create_and_get(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """템플릿 생성 및 조회 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 레이아웃 생성
    layout = await layout_service.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    # 파셜 생성
    partial = await partial_service.create(
        user,
        PartialCreate(
            name="test_partial",
            content="test partial content",
            description="test partial description",
            dependencies=set(),
        ),
    )

    # 템플릿 생성
    created_component = await template_service.create_component(
        user,
        "test",
        TemplateComponentCreate(
            component=TemplateComponents.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 생성된 템플릿 검증
    assert created_component.layout == layout.name
    assert created_component.partials == [partial.name]
    assert created_component.content == "test content"
    assert created_component.description == "test description"
    assert created_component.component == TemplateComponents.HTML_EMAIL.value
    assert created_component.template == "test"
    assert created_component.updated_at is not None
    assert created_component.updated_by == user.name
    assert created_component.created_at is not None
    assert created_component.created_by == user.name

    # 템플릿 조회
    get_component = await template_service.get_component(
        created_component.template, created_component.component
    )
    assert get_component.layout == created_component.layout
    assert get_component.partials == created_component.partials
    assert get_component.content == created_component.content
    assert get_component.description == created_component.description
    assert get_component.component == created_component.component
    assert get_component.template == created_component.template


@pytest.mark.asyncio
async def test_template_service_duplicate(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """중복 템플릿 생성 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 레이아웃 생성
    layout = await layout_service.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    # 파셜 생성
    partial = await partial_service.create(
        user,
        PartialCreate(
            name="test_partial",
            content="test partial content",
            description="test partial description",
            dependencies=set(),
        ),
    )

    # 템플릿 생성
    created_component = TemplateComponentCreate(
        component=TemplateComponents.HTML_EMAIL.value,
        description="test description",
        layout=layout.name,
        partials=[partial.name],
        content="test content",
    )
    await template_service.create_component(user, "test", created_component)

    # 중복 생성 시도
    with pytest.raises(TemplateAlreadyExistsError):
        await template_service.create_component(user, "test", created_component)


@pytest.mark.asyncio
async def test_template_service_not_found(version_info: VersionInfo, temp_env: TemplyEnv):
    """존재하지 않는 템플릿 조회 테스트"""
    template_service = TemplateService(TemplateRepository(version_info, temp_env))
    with pytest.raises(TemplateNotFoundError):
        await template_service.get_component("non_existent_template", "non_existent_component")


@pytest.mark.asyncio
async def test_template_service_update(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 레이아웃 생성
    layout = await layout_service.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    # 파셜 생성
    partial = await partial_service.create(
        user,
        PartialCreate(
            name="test_partial",
            content="test partial content",
            description="test partial description",
            dependencies=set(),
        ),
    )

    # 템플릿 생성
    created_component = await template_service.create_component(
        user,
        "test",
        TemplateComponentCreate(
            component=TemplateComponents.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 업데이트
    update_content = "updated content"
    update_description = "updated description"
    updated_component = await template_service.update_component(
        user,
        created_component.template,
        created_component.component,
        TemplateComponentUpdate(
            content=update_content,
            description=update_description,
            layout=layout.name,
            partials=[partial.name],
        ),
    )

    assert updated_component.content == update_content
    assert updated_component.description == update_description
    assert updated_component.created_at == created_component.created_at
    assert updated_component.created_by == created_component.created_by
    assert updated_component.updated_at is not None
    assert updated_component.updated_by == user.name


@pytest.mark.asyncio
async def test_template_service_delete(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """템플릿 삭제 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 레이아웃 생성
    layout = await layout_service.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    # 파셜 생성
    partial = await partial_service.create(
        user,
        PartialCreate(
            name="test_partial",
            content="test partial content",
            description="test partial description",
            dependencies=set(),
        ),
    )

    # 템플릿 생성
    created_component = await template_service.create_component(
        user,
        "test",
        TemplateComponentCreate(
            component=TemplateComponents.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 삭제
    await template_service.delete_component(
        user, created_component.template, created_component.component
    )

    # 삭제 확인
    with pytest.raises(TemplateNotFoundError):
        await template_service.get_component(
            created_component.template, created_component.component
        )


@pytest.mark.asyncio
async def test_template_service_nonexistent_layout(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """존재하지 않는 레이아웃 참조 테스트"""
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 파셜 생성
    partial = await partial_service.create(
        user,
        PartialCreate(
            name="test_partial",
            content="test partial content",
            description="test partial description",
            dependencies=set(),
        ),
    )

    # 존재하지 않는 레이아웃으로 템플릿 생성 시도
    with pytest.raises(LayoutNotFoundError):
        await template_service.create_component(
            user,
            "test",
            TemplateComponentCreate(
                component=TemplateComponents.HTML_EMAIL.value,
                description="test description",
                layout="nonexistent_layout",
                partials=[partial.name],
                content="test content",
            ),
        )


@pytest.mark.asyncio
async def test_template_service_nonexistent_partial(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """존재하지 않는 파셜 참조 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 레이아웃 생성
    layout = await layout_service.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    # 존재하지 않는 파셜로 템플릿 생성 시도
    with pytest.raises(PartialNotFoundError):
        await template_service.create_component(
            user,
            "test",
            TemplateComponentCreate(
                component=TemplateComponents.HTML_EMAIL.value,
                description="test description",
                layout=layout.name,
                partials=["nonexistent_partial"],
                content="test content",
            ),
        )


@pytest.mark.asyncio
async def test_template_service_update_layout(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """템플릿 업데이트 시 레이아웃 변경 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 기존 레이아웃 생성
    old_layout = await layout_service.create(
        user,
        LayoutCreate(
            name="old_layout",
            content="old layout content",
            description="old layout description",
        ),
    )

    # 새 레이아웃 생성
    new_layout = await layout_service.create(
        user,
        LayoutCreate(
            name="new_layout",
            content="new layout content",
            description="new layout description",
        ),
    )

    # 파셜 생성
    partial = await partial_service.create(
        user,
        PartialCreate(
            name="test_partial",
            content="test partial content",
            description="test partial description",
            dependencies=set(),
        ),
    )

    # 템플릿 생성
    created_component = await template_service.create_component(
        user,
        "test",
        TemplateComponentCreate(
            component=TemplateComponents.HTML_EMAIL.value,
            description="test description",
            layout=old_layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 레이아웃 변경
    updated_component = await template_service.update_component(
        user,
        created_component.template,
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


@pytest.mark.asyncio
async def test_template_service_update_partials(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """템플릿 업데이트 시 파셜 변경 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 레이아웃 생성
    layout = await layout_service.create(
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
        partial = await partial_service.create(
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
        partial = await partial_service.create(
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
    created_component = await template_service.create_component(
        user,
        "test",
        TemplateComponentCreate(
            component=TemplateComponents.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[p.name for p in old_partials],
            content="test content",
        ),
    )

    # 파셜 변경
    updated_component = await template_service.update_component(
        user,
        created_component.template,
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


@pytest.mark.asyncio
async def test_template_service_with_multiple_partials(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """여러 파셜을 사용하는 템플릿 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 레이아웃 생성
    layout = await layout_service.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    # 여러 파셜 생성
    partials = []
    for i in range(3):
        partial = await partial_service.create(
            user,
            PartialCreate(
                name=f"test_partial_{i}",
                content=f"test partial content {i}",
                description=f"test partial description {i}",
                dependencies=set(),
            ),
        )
        partials.append(partial)

    # 템플릿 생성
    created_component = await template_service.create_component(
        user,
        "test",
        TemplateComponentCreate(
            component=TemplateComponents.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[p.name for p in partials],
            content="test content",
        ),
    )

    # 생성된 템플릿 검증
    get_component = await template_service.get_component(
        created_component.template, created_component.component
    )
    assert get_component.partials is not None
    assert len(get_component.partials) == len(partials)
    for partial in partials:
        assert partial.name in get_component.partials


@pytest.mark.asyncio
async def test_template_service_with_nested_partials(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """중첩된 파셜을 사용하는 템플릿 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    template_service = TemplateService(TemplateRepository(version_info, temp_env))

    # 레이아웃 생성
    layout = await layout_service.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="test layout content",
            description="test layout description",
        ),
    )

    # 기본 파셜 생성
    base_partial = await partial_service.create(
        user,
        PartialCreate(
            name="base_partial",
            content="base content",
            description="base description",
            dependencies=set(),
        ),
    )

    # 기본 파셜을 의존하는 파셜 생성
    dependent_partial = await partial_service.create(
        user,
        PartialCreate(
            name="dependent_partial",
            content="dependent content",
            description="dependent description",
            dependencies={base_partial.name},
        ),
    )

    # 템플릿 생성
    created_component = await template_service.create_component(
        user,
        "test",
        TemplateComponentCreate(
            component=TemplateComponents.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[base_partial.name, dependent_partial.name],
            content="test content",
        ),
    )

    # 생성된 템플릿 검증
    get_component = await template_service.get_component(
        created_component.template, created_component.component
    )
    assert get_component.partials is not None
    assert base_partial.name in get_component.partials
    assert dependent_partial.name in get_component.partials


@pytest.mark.asyncio
async def test_template_service_get_template_names(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """템플릿 목록 조회 테스트"""
    template_service = TemplateService(TemplateRepository(version_info, temp_env))
    component_name = TemplateComponents.HTML_EMAIL.value
    created_component = TemplateComponentCreate(
        component=component_name,
        content="test content",
        description="test description",
        layout=None,
        partials=None,
    )

    # 템플릿 생성
    await template_service.create_component(user, "test", created_component)

    # 템플릿 목록 조회
    components = await template_service.get_component_names_by_template("test")
    assert component_name in components


@pytest.mark.asyncio
async def test_template_service_get_components_by_template(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """템플릿별 템플릿 목록 조회 테스트"""
    template_service = TemplateService(TemplateRepository(version_info, temp_env))
    component_name = TemplateComponents.HTML_EMAIL.value
    created_component = TemplateComponentCreate(
        component=component_name,
        content="test content",
        description="test description",
        layout=None,
        partials=None,
    )

    # 템플릿 생성
    await template_service.create_component(user, "test", created_component)

    # 카테고리별 템플릿 목록 조회
    components = await template_service.get_components_by_template("test")
    assert len(components) == 1
    assert components[0].component == component_name


@pytest.mark.asyncio
async def test_template_service_delete_components_by_template(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """템플릿별 템플릿 삭제 테스트"""
    template_service = TemplateService(TemplateRepository(version_info, temp_env))
    component_name = TemplateComponents.HTML_EMAIL.value
    created_component = TemplateComponentCreate(
        component=component_name,
        content="test content",
        description="test description",
        layout=None,
        partials=None,
    )

    # 템플릿 생성
    await template_service.create_component(user, "test", created_component)

    # 카테고리별 템플릿 삭제
    await template_service.delete_components_by_template(user, "test")

    # 템플릿이 삭제되었는지 확인
    with pytest.raises(TemplateNotFoundError):
        await template_service.get_component("test", component_name)

    # 카테고리별 템플릿 목록이 비어있는지 확인
    components = await template_service.get_components_by_template("test")
    assert len(components) == 0
