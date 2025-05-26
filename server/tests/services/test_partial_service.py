"""파셜 서비스 테스트"""

import asyncio

import pytest

from app.core.exceptions import PartialCircularDependencyError, PartialNotFoundError
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User, VersionInfo
from app.models.partial_model import PartialCreate, PartialUpdate
from app.repositories.partial_repository import PartialRepository
from app.services.partial_service import PartialService


def get_temp_env_service(version_info: VersionInfo, temp_env: TemplyEnv):
    """레이아웃 서비스 픽스처"""
    repository = PartialRepository(version_info, temp_env)
    service = PartialService(repository)
    return service


@pytest.mark.asyncio
async def test_partial_service_create_and_get(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """파셜 생성/조회 테스트"""
    service = get_temp_env_service(version_info, temp_env)
    # 파셜 생성
    partial_create = PartialCreate(
        name="test_partial",
        content="test content",
        description="test description",
        dependencies=set(),
    )
    created_partial = await service.create(user, partial_create)
    assert created_partial is not None
    assert created_partial.name == partial_create.name
    assert created_partial.content == partial_create.content
    assert created_partial.description == partial_create.description
    assert created_partial.dependencies == partial_create.dependencies
    assert created_partial.created_at is not None
    assert created_partial.created_by == user.name
    assert created_partial.updated_at is not None
    assert created_partial.updated_by == user.name

    # 파셜 조회
    retrieved_partial = await service.get(created_partial.name)
    assert retrieved_partial is not None
    assert retrieved_partial.name == created_partial.name
    assert retrieved_partial.content == created_partial.content
    assert retrieved_partial.description == created_partial.description
    assert retrieved_partial.dependencies == created_partial.dependencies


@pytest.mark.asyncio
async def test_partial_service_list(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """파셜 목록 조회 테스트"""
    service = get_temp_env_service(version_info, temp_env)
    # 여러 파셜 생성
    partials = []
    for i in range(3):
        partial_create = PartialCreate(
            name=f"test_partial_{i}",
            content=f"test content {i}",
            description=f"test description {i}",
            dependencies=set(),
        )
        partials.append(await service.create(user, partial_create))

    # 파셜 목록 조회
    retrieved_partials = await service.list()
    assert len(retrieved_partials) >= len(partials)
    for partial in partials:
        assert any(p.name == partial.name for p in retrieved_partials)


@pytest.mark.asyncio
async def test_partial_service_update(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """파셜 수정 테스트"""
    service = get_temp_env_service(version_info, temp_env)
    # 파셜 생성
    partial_create = PartialCreate(
        name="test_partial",
        content="test content",
        description="test description",
        dependencies=set(),
    )
    created_partial = await service.create(user, partial_create)
    assert created_partial is not None

    await asyncio.sleep(1)

    update_user = User(name="update_user")
    # 파셜 수정
    update_data = PartialUpdate(
        content="updated content",
        description="updated description",
        dependencies=set(),
    )
    updated_partial = await service.update(update_user, created_partial.name, update_data)
    assert updated_partial is not None
    assert updated_partial.name == created_partial.name
    assert updated_partial.content == update_data.content
    assert updated_partial.description == update_data.description
    assert updated_partial.dependencies == update_data.dependencies
    assert updated_partial.created_at == created_partial.created_at
    assert updated_partial.created_by == created_partial.created_by
    assert updated_partial.updated_at is not None
    assert updated_partial.updated_by == update_user.name


@pytest.mark.asyncio
async def test_partial_service_delete(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """파셜 삭제 테스트"""
    service = get_temp_env_service(version_info, temp_env)
    # 파셜 생성
    partial_create = PartialCreate(
        name="test_partial",
        content="test content",
        description="test description",
        dependencies=set(),
    )
    created_partial = await service.create(user, partial_create)
    assert created_partial is not None

    # 파셜 삭제
    await service.delete(user, created_partial.name)

    # 삭제 확인
    with pytest.raises(PartialNotFoundError):
        await service.get(created_partial.name)


@pytest.mark.asyncio
async def test_partial_service_not_found(version_info: VersionInfo, temp_env: TemplyEnv):
    """존재하지 않는 파셜 조회 테스트"""
    service = get_temp_env_service(version_info, temp_env)
    with pytest.raises(PartialNotFoundError):
        await service.get("non_existent_partial")


@pytest.fixture
async def partial_with_dependency(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """의존성이 있는 파셜을 생성하는 fixture"""
    service = get_temp_env_service(version_info, temp_env)

    # 기본 파셜 생성
    base_partial = await service.create(
        user,
        PartialCreate(
            name="base_partial",
            content="base content",
            description="base description",
            dependencies=set(),
        ),
    )

    # 의존하는 파셜 생성
    dependent_partial = await service.create(
        user,
        PartialCreate(
            name="dependent_partial",
            content="dependent content",
            description="dependent description",
            dependencies={base_partial.name},
        ),
    )

    return service, base_partial, dependent_partial


@pytest.mark.asyncio
async def test_partial_service_circular_dependencies(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """순환 의존성 테스트"""
    service = get_temp_env_service(version_info, temp_env)

    # 두 파셜을 의존성 없이 생성
    partial1 = await service.create(
        user,
        PartialCreate(
            name="partial1",
            content="content1",
            description="description1",
            dependencies=set(),
        ),
    )
    assert partial1 is not None

    partial2 = await service.create(
        user,
        PartialCreate(
            name="partial2",
            content="content2",
            description="description2",
            dependencies=set(),
        ),
    )
    assert partial2 is not None

    # partial2가 partial1에 의존하도록 업데이트
    updated_partial2 = await service.update(
        user,
        partial2.name,
        PartialUpdate(
            content="content2",
            description="description2",
            dependencies={partial1.name},
        ),
    )
    assert updated_partial2 is not None
    assert partial1.name in updated_partial2.dependencies

    # 순환 의존성 생성 시도 (partial1이 partial2에 의존하도록 업데이트)
    with pytest.raises(
        PartialCircularDependencyError,
        match="Circular dependency detected: partial1 -> partial2 -> partial1",
    ):
        await service.update(
            user,
            partial1.name,
            PartialUpdate(
                content="updated content",
                description="updated description",
                dependencies={partial2.name},  # 순환 의존성 생성
            ),
        )


@pytest.mark.asyncio
async def test_partial_service_update_dependencies(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """의존성 업데이트 테스트"""
    service = get_temp_env_service(version_info, temp_env)

    # 기본 파셜 생성
    base_partial = await service.create(
        user,
        PartialCreate(
            name="base_partial",
            content="base content",
            description="base description",
            dependencies=set(),
        ),
    )

    # 의존하는 파셜 생성
    dependent_partial = await service.create(
        user,
        PartialCreate(
            name="dependent_partial",
            content="dependent content",
            description="dependent description",
            dependencies={base_partial.name},
        ),
    )

    # 새 파셜 생성
    new_partial = await service.create(
        user,
        PartialCreate(
            name="new_partial",
            content="new content",
            description="new description",
            dependencies=set(),
        ),
    )

    # 존재하지 않는 의존성으로 업데이트 시도
    with pytest.raises(PartialNotFoundError):
        await service.update(
            user,
            dependent_partial.name,
            PartialUpdate(
                content="dependent content",
                description="dependent description",
                dependencies={"nonexistent_partial"},
            ),
        )

    # 의존성 업데이트
    updated_partial = await service.update(
        user,
        dependent_partial.name,
        PartialUpdate(
            content="dependent content",
            description="dependent description",
            dependencies={base_partial.name, new_partial.name},
        ),
    )

    assert base_partial.name in updated_partial.dependencies
    assert new_partial.name in updated_partial.dependencies


@pytest.mark.asyncio
async def test_partial_service_get_root(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """루트 파셜 조회 테스트"""
    partial_service = PartialService(PartialRepository(version_info, temp_env))

    # 루트 파셜 생성
    root_partial = await partial_service.create(
        user,
        PartialCreate(
            name="root_partial",
            content="root content",
            description="root description",
            dependencies=set(),
        ),
    )

    # 의존성이 있는 파셜 생성
    dependent_partial = await partial_service.create(
        user,
        PartialCreate(
            name="dependent_partial",
            content="dependent content",
            description="dependent description",
            dependencies={root_partial.name},
        ),
    )

    # 루트 파셜 조회
    root_partials = await partial_service.get_root()
    assert len(root_partials) == 1
    assert root_partials[0].name == root_partial.name
    assert root_partials[0].content == root_partial.content
    assert root_partials[0].description == root_partial.description
    assert root_partials[0].dependencies == set()


@pytest.mark.asyncio
async def test_partial_service_get_children(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """자식 파셜 조회 테스트"""
    partial_service = PartialService(PartialRepository(version_info, temp_env))

    # 부모 파셜 생성
    parent_partial = await partial_service.create(
        user,
        PartialCreate(
            name="parent_partial",
            content="parent content",
            description="parent description",
            dependencies=set(),
        ),
    )

    # 자식 파셜들 생성
    child_partials = []
    for i in range(2):
        child = await partial_service.create(
            user,
            PartialCreate(
                name=f"child_partial_{i}",
                content=f"child content {i}",
                description=f"child description {i}",
                dependencies={parent_partial.name},
            ),
        )
        child_partials.append(child)

    # 자식 파셜 조회
    children = await partial_service.get_children(parent_partial.name)
    assert len(children) == len(child_partials)
    for child in children:
        assert any(c.name == child.name for c in child_partials)
        assert any(c.content == child.content for c in child_partials)
        assert any(c.description == child.description for c in child_partials)
        assert parent_partial.name in child.dependencies


@pytest.mark.asyncio
async def test_partial_service_get_children_not_found(
    version_info: VersionInfo, temp_env: TemplyEnv
):
    """존재하지 않는 파셜의 자식 조회 테스트"""
    partial_service = PartialService(PartialRepository(version_info, temp_env))
    with pytest.raises(PartialNotFoundError):
        await partial_service.get_children("non_existent_partial")
