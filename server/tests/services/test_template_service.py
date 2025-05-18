"""템플릿 서비스 테스트"""

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
from app.services.layout_service import LayoutService
from app.services.partial_service import PartialService
from app.services.template_service import TemplateService


@pytest.mark.asyncio
async def test_template_service_create_and_get(temp_env: TemplyEnv, user: User):
    """템플릿 생성 및 조회 테스트"""
    layout_service = LayoutService(LayoutRepository(temp_env))
    partial_service = PartialService(PartialRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
    template = await template_service.create(
        user,
        TemplateCreate(
            category="test",
            name=TemplateItems.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 생성된 템플릿 검증
    assert template.layout == layout.name
    assert template.partials == [partial.name]
    assert template.content == "test content"
    assert template.description == "test description"
    assert template.name == TemplateItems.HTML_EMAIL.value
    assert template.category == "test"
    assert template.updated_at is not None
    assert template.updated_by == user.name
    assert template.created_at is not None
    assert template.created_by == user.name

    # 템플릿 조회
    get_template = await template_service.get(template.category, template.name)
    assert get_template.layout == template.layout
    assert get_template.partials == template.partials
    assert get_template.content == template.content
    assert get_template.description == template.description
    assert get_template.name == template.name
    assert get_template.category == template.category


@pytest.mark.asyncio
async def test_template_service_duplicate(temp_env: TemplyEnv, user: User):
    """중복 템플릿 생성 테스트"""
    layout_service = LayoutService(LayoutRepository(temp_env))
    partial_service = PartialService(PartialRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
    template_create = TemplateCreate(
        category="test",
        name=TemplateItems.HTML_EMAIL.value,
        description="test description",
        layout=layout.name,
        partials=[partial.name],
        content="test content",
    )
    await template_service.create(user, template_create)

    # 중복 생성 시도
    with pytest.raises(TemplateAlreadyExistsError):
        await template_service.create(user, template_create)


@pytest.mark.asyncio
async def test_template_service_not_found(temp_env: TemplyEnv):
    """존재하지 않는 템플릿 조회 테스트"""
    template_service = TemplateService(TemplateRepository(temp_env))
    with pytest.raises(TemplateNotFoundError):
        await template_service.get("non_existent_category", "non_existent_template")


@pytest.mark.asyncio
async def test_template_service_update(temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 테스트"""
    layout_service = LayoutService(LayoutRepository(temp_env))
    partial_service = PartialService(PartialRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
    template = await template_service.create(
        user,
        TemplateCreate(
            category="test",
            name=TemplateItems.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 업데이트
    update_content = "updated content"
    update_description = "updated description"
    updated_template = await template_service.update(
        user,
        template.category,
        template.name,
        TemplateUpdate(
            content=update_content,
            description=update_description,
            layout=layout.name,
            partials=[partial.name],
        ),
    )

    assert updated_template.content == update_content
    assert updated_template.description == update_description
    assert updated_template.created_at == template.created_at
    assert updated_template.created_by == template.created_by
    assert updated_template.updated_at is not None
    assert updated_template.updated_by == user.name


@pytest.mark.asyncio
async def test_template_service_delete(temp_env: TemplyEnv, user: User):
    """템플릿 삭제 테스트"""
    layout_service = LayoutService(LayoutRepository(temp_env))
    partial_service = PartialService(PartialRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
    template = await template_service.create(
        user,
        TemplateCreate(
            category="test",
            name=TemplateItems.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 삭제
    await template_service.delete(user, template.category, template.name)

    # 삭제 확인
    with pytest.raises(TemplateNotFoundError):
        await template_service.get(template.category, template.name)


@pytest.mark.asyncio
async def test_template_service_nonexistent_layout(temp_env: TemplyEnv, user: User):
    """존재하지 않는 레이아웃 참조 테스트"""
    partial_service = PartialService(PartialRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
        await template_service.create(
            user,
            TemplateCreate(
                category="test",
                name=TemplateItems.HTML_EMAIL.value,
                description="test description",
                layout="nonexistent_layout",
                partials=[partial.name],
                content="test content",
            ),
        )


@pytest.mark.asyncio
async def test_template_service_nonexistent_partial(temp_env: TemplyEnv, user: User):
    """존재하지 않는 파셜 참조 테스트"""
    layout_service = LayoutService(LayoutRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
        await template_service.create(
            user,
            TemplateCreate(
                category="test",
                name=TemplateItems.HTML_EMAIL.value,
                description="test description",
                layout=layout.name,
                partials=["nonexistent_partial"],
                content="test content",
            ),
        )


@pytest.mark.asyncio
async def test_template_service_update_layout(temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 시 레이아웃 변경 테스트"""
    layout_service = LayoutService(LayoutRepository(temp_env))
    partial_service = PartialService(PartialRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
    template = await template_service.create(
        user,
        TemplateCreate(
            category="test",
            name=TemplateItems.HTML_EMAIL.value,
            description="test description",
            layout=old_layout.name,
            partials=[partial.name],
            content="test content",
        ),
    )

    # 레이아웃 변경
    updated_template = await template_service.update(
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


@pytest.mark.asyncio
async def test_template_service_update_partials(temp_env: TemplyEnv, user: User):
    """템플릿 업데이트 시 파셜 변경 테스트"""
    layout_service = LayoutService(LayoutRepository(temp_env))
    partial_service = PartialService(PartialRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
    template = await template_service.create(
        user,
        TemplateCreate(
            category="test",
            name=TemplateItems.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[p.name for p in old_partials],
            content="test content",
        ),
    )

    # 파셜 변경
    updated_template = await template_service.update(
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


@pytest.mark.asyncio
async def test_template_service_with_multiple_partials(temp_env: TemplyEnv, user: User):
    """여러 파셜을 사용하는 템플릿 테스트"""
    layout_service = LayoutService(LayoutRepository(temp_env))
    partial_service = PartialService(PartialRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
    template = await template_service.create(
        user,
        TemplateCreate(
            category="test",
            name=TemplateItems.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[p.name for p in partials],
            content="test content",
        ),
    )

    # 생성된 템플릿 검증
    get_template = await template_service.get(template.category, template.name)
    assert get_template.partials is not None
    assert len(get_template.partials) == len(partials)
    for partial in partials:
        assert partial.name in get_template.partials


@pytest.mark.asyncio
async def test_template_service_with_nested_partials(temp_env: TemplyEnv, user: User):
    """중첩된 파셜을 사용하는 템플릿 테스트"""
    layout_service = LayoutService(LayoutRepository(temp_env))
    partial_service = PartialService(PartialRepository(temp_env))
    template_service = TemplateService(TemplateRepository(temp_env))

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
    template = await template_service.create(
        user,
        TemplateCreate(
            category="test",
            name=TemplateItems.HTML_EMAIL.value,
            description="test description",
            layout=layout.name,
            partials=[base_partial.name, dependent_partial.name],
            content="test content",
        ),
    )

    # 생성된 템플릿 검증
    get_template = await template_service.get(template.category, template.name)
    assert get_template.partials is not None
    assert base_partial.name in get_template.partials
    assert dependent_partial.name in get_template.partials
