"""레이아웃 리포지토리 테스트"""

import pytest

from app.core.exceptions import LayoutAlreadyExistsError, LayoutNotFoundError
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User, VersionInfo
from app.models.layout_model import LayoutCreate, LayoutUpdate
from app.repositories.layout_repository import LayoutRepository


@pytest.mark.asyncio
async def test_layout_repository(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """기본 레이아웃 생성/조회 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    layout_create = LayoutCreate(
        name="test_layout",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)
    assert create_layout.name == layout_create.name
    assert create_layout.content == layout_create.content
    assert create_layout.description == layout_create.description
    assert create_layout.created_at is not None
    assert create_layout.created_by == user.name
    assert create_layout.updated_at is not None
    assert create_layout.updated_by == user.name

    get_layout = await layout_repository.get(create_layout.name)
    assert get_layout.name == create_layout.name
    assert get_layout.content == create_layout.content
    assert get_layout.description == create_layout.description


@pytest.mark.asyncio
async def test_layout_duplicate(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """중복 레이아웃 생성 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    layout_create = LayoutCreate(
        name="test_layout",
        content="test layout content",
        description="test layout description",
    )
    await layout_repository.create(user, layout_create)
    with pytest.raises(LayoutAlreadyExistsError):
        await layout_repository.create(user, layout_create)


@pytest.mark.asyncio
async def test_layout_not_found(version_info: VersionInfo, temp_env: TemplyEnv):
    """존재하지 않는 레이아웃 조회 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    with pytest.raises(LayoutNotFoundError):
        await layout_repository.get("non_existent_layout")


@pytest.mark.asyncio
async def test_layout_update(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """레이아웃 업데이트 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    layout_create = LayoutCreate(
        name="test_layout",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)

    # 업데이트
    update_content = "updated content"
    update_description = "updated description"
    update_layout = await layout_repository.update(
        user,
        create_layout.name,
        LayoutUpdate(
            content=update_content,
            description=update_description,
        ),
    )
    assert update_layout.content == update_content
    assert update_layout.description == update_description
    assert update_layout.created_at == create_layout.created_at
    assert update_layout.created_by == create_layout.created_by
    assert update_layout.updated_at is not None
    assert update_layout.updated_by == user.name

    # 업데이트된 레이아웃 조회
    get_layout = await layout_repository.get(create_layout.name)
    assert get_layout.content == update_content
    assert get_layout.description == update_description


@pytest.mark.asyncio
async def test_layout_invalid_name(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """잘못된 레이아웃 이름 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    invalid_names = [
        "test/layout",  # 슬래시 포함
        "test layout",  # 공백 포함
        "test:layout",  # 콜론 포함
        "test*layout",  # 별표 포함
        "test?layout",  # 물음표 포함
        'test"layout',  # 따옴표 포함
        "test<layout",  # 꺾쇠 포함
        "test>layout",  # 꺾쇠 포함
        "test|layout",  # 파이프 포함
    ]

    for invalid_name in invalid_names:
        with pytest.raises(ValueError):
            await layout_repository.create(
                user,
                LayoutCreate(
                    name=invalid_name,
                    content="test content",
                    description="test description",
                ),
            )


@pytest.mark.asyncio
async def test_layout_delete(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """레이아웃 삭제 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    layout_create = LayoutCreate(
        name="test_layout",
        content="test layout content",
        description="test layout description",
    )
    create_layout = await layout_repository.create(user, layout_create)
    await layout_repository.delete(user, create_layout.name)

    # 삭제 확인
    with pytest.raises(LayoutNotFoundError):
        await layout_repository.get(create_layout.name)


@pytest.mark.asyncio
async def test_layout_with_block(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """블록이 포함된 레이아웃 생성 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    layout_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{% block title %}{% endblock %}</title>
    </head>
    <body>
        <header>{% block header %}{% endblock %}</header>
        <main>{% block content %}{% endblock %}</main>
        <footer>{% block footer %}{% endblock %}</footer>
    </body>
    </html>
    """
    layout_create = LayoutCreate(
        name="test_layout",
        content=layout_content,
        description="test layout with blocks",
    )
    create_layout = await layout_repository.create(user, layout_create)

    # 생성된 레이아웃 검증
    get_layout = await layout_repository.get(create_layout.name)
    assert "{% block title %}" in get_layout.content
    assert "{% block header %}" in get_layout.content
    assert "{% block content %}" in get_layout.content
    assert "{% block footer %}" in get_layout.content


@pytest.mark.asyncio
async def test_layout_with_extends(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """상속이 포함된 레이아웃 생성 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)

    # 기본 레이아웃 생성
    base_layout = await layout_repository.create(
        user,
        LayoutCreate(
            name="base_layout",
            content="{% block content %}{% endblock %}",
            description="base layout",
        ),
    )

    # 상속받는 레이아웃 생성
    child_layout = await layout_repository.create(
        user,
        LayoutCreate(
            name="child_layout",
            content="{% extends 'layouts/base_layout' %}\n{% block content %}Child content{% endblock %}",
            description="child layout",
        ),
    )

    # 상속 관계 검증
    get_child = await layout_repository.get(child_layout.name)
    assert "{% extends 'layouts/base_layout' %}" in get_child.content
    assert "{% block content %}Child content{% endblock %}" in get_child.content


@pytest.mark.asyncio
async def test_layout_multiple(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """여러 레이아웃 생성/조회 테스트"""
    layout_repository = LayoutRepository(version_info, temp_env)
    layouts = []

    # 여러 레이아웃 생성
    for i in range(3):
        layout_create = LayoutCreate(
            name=f"test_layout_{i}",
            content=f"test layout content {i}",
            description=f"test layout description {i}",
        )
        layouts.append(await layout_repository.create(user, layout_create))

    # 생성된 레이아웃 검증
    for i, layout in enumerate(layouts):
        get_layout = await layout_repository.get(layout.name)
        assert get_layout.name == f"test_layout_{i}"
        assert get_layout.content == f"test layout content {i}"
        assert get_layout.description == f"test layout description {i}"
        assert get_layout.created_at is not None
        assert get_layout.created_by == user.name
        assert get_layout.updated_at is not None
        assert get_layout.updated_by == user.name

    # 파일 내용 검증
    for layout in layouts:
        content, _, _ = temp_env.load_layout_source(layout.name)
        assert layout.content in content
        if layout.description:
            assert layout.description in content
