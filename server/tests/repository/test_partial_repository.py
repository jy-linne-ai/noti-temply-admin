"""파셜 리포지토리 테스트"""

import asyncio

import pytest

from app.core.exceptions import PartialAlreadyExistsError, PartialNotFoundError
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User
from app.models.partial_model import PartialCreate, PartialUpdate
from app.repositories.partial_repository import PartialRepository


@pytest.mark.asyncio
async def test_partial_repository(temp_env: TemplyEnv, user: User):
    """기본 파셜 생성/조회 테스트"""
    partial_repository = PartialRepository(temp_env)
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
async def test_partial_duplicate(temp_env: TemplyEnv, user: User):
    """중복 파셜 생성 테스트"""
    partial_repository = PartialRepository(temp_env)
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
async def test_partial_not_found(temp_env: TemplyEnv):
    """존재하지 않는 파셜 조회 테스트"""
    partial_repository = PartialRepository(temp_env)
    with pytest.raises(PartialNotFoundError):
        await partial_repository.get("non_existent_partial")


@pytest.mark.asyncio
async def test_partial_update(temp_env: TemplyEnv, user: User):
    """파셜 업데이트 테스트"""
    partial_repository = PartialRepository(temp_env)
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
async def test_partial_with_dependencies(temp_env: TemplyEnv, user: User):
    """의존성이 있는 파셜 생성 테스트"""
    partial_repository = PartialRepository(temp_env)

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
async def test_partial_invalid_name(temp_env: TemplyEnv, user: User):
    """잘못된 파셜 이름 테스트"""
    partial_repository = PartialRepository(temp_env)
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
async def test_partial_delete(temp_env: TemplyEnv, user: User):
    """파셜 삭제 테스트"""
    partial_repository = PartialRepository(temp_env)
    partial_create = PartialCreate(
        name="test_partial",
        content="test partial content",
        description="test partial description",
        dependencies=set(),
    )
    create_partial = await partial_repository.create(user, partial_create)

    # 삭제
    await partial_repository.delete(create_partial.name)

    # 삭제 확인
    with pytest.raises(PartialNotFoundError):
        await partial_repository.get(create_partial.name)


@pytest.mark.asyncio
async def test_partial_repository_with_dependencies(temp_env: TemplyEnv, user: User):
    """Test partial repository with dependencies"""
    partial_repository = PartialRepository(temp_env)

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
    load_content, _, _ = temp_env.get_source_partial(test3_partial.name)
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
