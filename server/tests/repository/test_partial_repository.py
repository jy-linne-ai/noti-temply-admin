"""파셜 리포지토리 테스트"""

import pytest

from app.core.exceptions import (
    PartialAlreadyExistsError,
    PartialCircularDependencyError,
    PartialNotFoundError,
)
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User, VersionInfo
from app.models.partial_model import PartialCreate, PartialUpdate
from app.repositories.partial_repository import PartialRepository


@pytest.mark.asyncio
async def test_partial_repository(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """기본 파셜 생성/조회 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)
    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)
    assert create_partial.name == partial_create.name
    assert create_partial.content == partial_create.content
    assert create_partial.description == partial_create.description
    assert create_partial.dependencies == partial_create.dependencies
    assert create_partial.created_at is not None
    assert create_partial.created_by == user.name
    assert create_partial.updated_at is not None
    assert create_partial.updated_by == user.name

    get_partial = await partial_repository.get(create_partial.name)
    assert get_partial.name == create_partial.name
    assert get_partial.content == create_partial.content
    assert get_partial.description == create_partial.description
    assert get_partial.dependencies == create_partial.dependencies


@pytest.mark.asyncio
async def test_partial_duplicate(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """중복 파셜 생성 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)
    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    await partial_repository.create(user, partial_create)
    with pytest.raises(PartialAlreadyExistsError):
        await partial_repository.create(user, partial_create)


@pytest.mark.asyncio
async def test_partial_not_found(version_info: VersionInfo, temp_env: TemplyEnv):
    """존재하지 않는 파셜 조회 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)
    with pytest.raises(PartialNotFoundError):
        await partial_repository.get("non_existent_partial")


@pytest.mark.asyncio
async def test_partial_update(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """파셜 업데이트 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)
    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    # 업데이트
    update_content = "updated content"
    update_description = "updated description"
    update_partial = await partial_repository.update(
        user,
        create_partial.name,
        PartialUpdate(
            content=update_content,
            description=update_description,
            dependencies=set(),
        ),
    )
    assert update_partial.content == update_content
    assert update_partial.description == update_description
    assert update_partial.created_at == create_partial.created_at
    assert update_partial.created_by == create_partial.created_by
    assert update_partial.updated_at is not None
    assert update_partial.updated_by == user.name


@pytest.mark.asyncio
async def test_partial_with_dependencies(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """의존성이 있는 파셜 생성 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)

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

    # 의존성이 있는 파셜 생성
    dependent_partial = await partial_repository.create(
        user,
        PartialCreate(
            name="dependent_partial",
            content="dependent content",
            description="dependent description",
            dependencies={base_partial.name},
        ),
    )

    assert base_partial.name in dependent_partial.dependencies

    # 의존성 검증
    get_dependent = await partial_repository.get(dependent_partial.name)
    assert base_partial.name in get_dependent.dependencies


@pytest.mark.asyncio
async def test_partial_invalid_name(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """잘못된 파셜 이름 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)
    invalid_names = [
        "test/partial",  # 슬래시 포함
        "test partial",  # 공백 포함
        "test:partial",  # 콜론 포함
        "test*partial",  # 별표 포함
        "test?partial",  # 물음표 포함
        'test"partial',  # 따옴표 포함
        "test<partial",  # 꺾쇠 포함
        "test>partial",  # 꺾쇠 포함
        "test|partial",  # 파이프 포함
    ]

    for invalid_name in invalid_names:
        with pytest.raises(ValueError):
            await partial_repository.create(
                user,
                PartialCreate(
                    name=invalid_name,
                    content="test content",
                    description="test description",
                    dependencies=set(),
                ),
            )


@pytest.mark.asyncio
async def test_partial_delete(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """파셜 삭제 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)
    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    # 삭제
    await partial_repository.delete(user, create_partial.name)

    # 삭제 확인
    with pytest.raises(PartialNotFoundError):
        await partial_repository.get(create_partial.name)


@pytest.mark.asyncio
async def test_partial_repository_with_dependencies(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """Test partial repository with dependencies"""
    partial_repository = PartialRepository(version_info, temp_env)

    test_partial = PartialCreate(
        name="test",
        content="test content",
        dependencies=set(),
        description="test description",
    )
    create_partial = await partial_repository.create(user, test_partial)
    assert create_partial.name == test_partial.name
    assert create_partial.content == test_partial.content
    assert create_partial.dependencies == test_partial.dependencies
    assert create_partial.description == test_partial.description
    assert create_partial.created_at is not None
    assert create_partial.created_by == user.name
    assert create_partial.updated_at is not None
    assert create_partial.updated_by == user.name

    test2_partial = PartialCreate(
        name="test2",
        content="test2 content",
        dependencies=set(),
        description="test2 description",
    )
    create_partial = await partial_repository.create(user, test2_partial)
    assert create_partial.name == test2_partial.name
    assert create_partial.content == test2_partial.content
    assert create_partial.dependencies == test2_partial.dependencies
    assert create_partial.description == test2_partial.description
    assert create_partial.created_at is not None
    assert create_partial.created_by == user.name
    assert create_partial.updated_at is not None
    assert create_partial.updated_by == user.name

    test3_partial = PartialCreate(
        name="test3",
        content="test3 content",
        dependencies=set([test_partial.name, test2_partial.name]),
        description="test3 description",
    )
    create_partial = await partial_repository.create(user, test3_partial)
    assert create_partial.name == test3_partial.name
    assert create_partial.content == test3_partial.content
    load_content, _, _ = temp_env.load_partial_source(test3_partial.name)
    print(load_content)
    assert (
        "{%- from 'partials/test' import render as partials_test with context -%}" in load_content
    )
    assert (
        "{%- from 'partials/test2' import render as partials_test2 with context -%}" in load_content
    )

    assert test_partial.name in create_partial.dependencies
    assert test2_partial.name in create_partial.dependencies

    get_partial = await partial_repository.get(test3_partial.name)
    assert get_partial.name == test3_partial.name
    assert get_partial.content == test3_partial.content
    assert get_partial.dependencies == test3_partial.dependencies
    assert get_partial.description == test3_partial.description
    assert get_partial.created_at is not None
    assert get_partial.created_by == user.name
    assert get_partial.updated_at is not None
    assert get_partial.updated_by == user.name


@pytest.mark.asyncio
async def test_partial_circular_dependency(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """순환 의존성 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)

    # 첫 번째 파셜 생성
    partial1 = await partial_repository.create(
        user,
        PartialCreate(
            name="partial1",
            content="content1",
            description="description1",
            dependencies=set(),
        ),
    )

    # 두 번째 파셜 생성 (partial1에 의존)
    partial2 = await partial_repository.create(
        user,
        PartialCreate(
            name="partial2",
            content="content2",
            description="description2",
            dependencies={partial1.name},
        ),
    )

    # 순환 의존성 시도 (partial1이 partial2에 의존하도록 업데이트)
    with pytest.raises(PartialCircularDependencyError, match="Circular dependency detected"):
        await partial_repository.update(
            user,
            partial1.name,
            PartialUpdate(
                content="updated content",
                description="updated description",
                dependencies={partial2.name},
            ),
        )


@pytest.mark.asyncio
async def test_partial_nonexistent_dependency(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """존재하지 않는 의존성 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)

    # 존재하지 않는 의존성을 가진 파셜 생성 시도
    with pytest.raises(PartialNotFoundError):
        await partial_repository.create(
            user,
            PartialCreate(
                name="test_partial",
                content="test content",
                description="test description",
                dependencies={"nonexistent_partial"},
            ),
        )


@pytest.mark.asyncio
async def test_partial_update_dependencies(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """파셜 업데이트 시 의존성 변경 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)

    # 기본 파셜들 생성
    base_partial = await partial_repository.create(
        user,
        PartialCreate(
            name="base_partial",
            content="base content",
            description="base description",
            dependencies=set(),
        ),
    )

    dependent_partial = await partial_repository.create(
        user,
        PartialCreate(
            name="dependent_partial",
            content="dependent content",
            description="dependent description",
            dependencies={base_partial.name},
        ),
    )

    # 새로운 의존성 추가
    new_dependencies = {base_partial.name, "new_dependency"}
    with pytest.raises(PartialNotFoundError):
        await partial_repository.update(
            user,
            dependent_partial.name,
            PartialUpdate(
                content="updated content",
                description="updated description",
                dependencies=new_dependencies,
            ),
        )

    # 새로운 파셜 생성 후 의존성 업데이트
    new_partial = await partial_repository.create(
        user,
        PartialCreate(
            name="new_dependency",
            content="new content",
            description="new description",
            dependencies=set(),
        ),
    )

    # 의존성 업데이트
    updated_partial = await partial_repository.update(
        user,
        dependent_partial.name,
        PartialUpdate(
            content="updated content",
            description="updated description",
            dependencies={base_partial.name, new_partial.name},
        ),
    )

    assert base_partial.name in updated_partial.dependencies
    assert new_partial.name in updated_partial.dependencies
    assert len(updated_partial.dependencies) == 2


@pytest.mark.asyncio
async def test_partial_repository_get_root(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """루트 파셜 조회 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)

    # 루트 파셜 생성
    root_partial = await partial_repository.create(
        user,
        PartialCreate(
            name="root_partial",
            content="root content",
            description="root description",
            dependencies=set(),
        ),
    )

    # 의존성이 있는 파셜 생성
    dependent_partial = await partial_repository.create(
        user,
        PartialCreate(
            name="dependent_partial",
            content="dependent content",
            description="dependent description",
            dependencies={root_partial.name},
        ),
    )

    # 루트 파셜 조회
    root_partials = await partial_repository.get_root()
    assert len(root_partials) == 1
    assert root_partials[0].name == root_partial.name
    assert root_partials[0].content == root_partial.content
    assert root_partials[0].description == root_partial.description
    assert root_partials[0].dependencies == set()


@pytest.mark.asyncio
async def test_partial_repository_get_children(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """자식 파셜 조회 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)

    # 부모 파셜 생성
    parent_partial = await partial_repository.create(
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
        child = await partial_repository.create(
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
    children = await partial_repository.get_children(parent_partial.name)
    assert len(children) == len(child_partials)
    for child in children:
        assert any(c.name == child.name for c in child_partials)
        assert any(c.content == child.content for c in child_partials)
        assert any(c.description == child.description for c in child_partials)
        assert parent_partial.name in child.dependencies


@pytest.mark.asyncio
async def test_partial_repository_get_children_not_found(
    version_info: VersionInfo, temp_env: TemplyEnv
):
    """존재하지 않는 파셜의 자식 조회 테스트"""
    partial_repository = PartialRepository(version_info, temp_env)
    with pytest.raises(PartialNotFoundError):
        await partial_repository.get_children("non_existent_partial")
