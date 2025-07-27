"""레이아웃 서비스 테스트"""

import asyncio

import pytest

from temply_app.core.exceptions import LayoutNotFoundError
from temply_app.core.temply.temply_env import TemplyEnv
from temply_app.models.common_model import User, VersionInfo
from temply_app.models.layout_model import LayoutCreate, LayoutUpdate
from temply_app.repositories.layout_repository import LayoutRepository
from temply_app.services.layout_service import LayoutService


def get_temp_env_service(version_info: VersionInfo, temp_env: TemplyEnv):
    """레이아웃 서비스 픽스처"""
    repository = LayoutRepository(version_info, temp_env)
    service = LayoutService(repository)
    return service


@pytest.mark.asyncio
async def test_layout_service_create_and_get(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """레이아웃 생성 및 조회 테스트"""
    # 레이아웃 생성
    service = get_temp_env_service(version_info, temp_env)
    layout_create = LayoutCreate(
        name="test_layout",
        content="test content",
        description="test description",
    )
    print(service)
    created_layout = await service.create(user, layout_create)
    assert created_layout is not None

    # 생성된 레이아웃 검증
    assert created_layout.name == layout_create.name
    assert created_layout.content == layout_create.content
    assert created_layout.description == layout_create.description
    assert created_layout.created_at is not None
    assert created_layout.created_by == user.name
    assert created_layout.updated_at is not None
    assert created_layout.updated_by == user.name

    # 레이아웃 조회
    retrieved_layout = await service.get(created_layout.name)
    assert retrieved_layout is not None
    assert retrieved_layout.name == created_layout.name
    assert retrieved_layout.content == created_layout.content
    assert retrieved_layout.description == created_layout.description


@pytest.mark.asyncio
async def test_layout_service_list(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """레이아웃 목록 조회 테스트"""
    service = get_temp_env_service(version_info, temp_env)
    # 여러 레이아웃 생성
    layouts = []
    for i in range(3):
        layout_create = LayoutCreate(
            name=f"test_layout_{i}",
            content=f"test content {i}",
            description=f"test description {i}",
        )
        layouts.append(await service.create(user, layout_create))

    # 레이아웃 목록 조회
    layout_list = await service.list()
    assert len(layout_list) == len(layouts)
    for layout in layouts:
        assert any(l.name == layout.name for l in layout_list)


@pytest.mark.asyncio
async def test_layout_service_update(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """레이아웃 수정 테스트"""
    service = get_temp_env_service(version_info, temp_env)
    # 레이아웃 생성
    layout_create = LayoutCreate(
        name="test_layout",
        content="test content",
        description="test description",
    )
    created_layout = await service.create(user, layout_create)
    assert created_layout is not None

    await asyncio.sleep(1)

    update_user = User(
        name="update_user",
    )
    # 레이아웃 수정
    update_data = LayoutUpdate(
        content="updated content",
        description="updated description",
    )
    updated_layout, _ = await service.update(update_user, created_layout.name, update_data)
    assert updated_layout is not None

    # 수정된 레이아웃 검증
    assert updated_layout.name == created_layout.name
    assert updated_layout.content == update_data.content
    assert updated_layout.description == update_data.description
    assert updated_layout.created_at == created_layout.created_at
    assert updated_layout.created_by == created_layout.created_by
    assert updated_layout.updated_at != created_layout.updated_at
    assert updated_layout.updated_by == update_user.name


@pytest.mark.asyncio
async def test_layout_service_delete(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """레이아웃 삭제 테스트"""
    service = get_temp_env_service(version_info, temp_env)
    # 레이아웃 생성
    layout_create = LayoutCreate(
        name="test_layout",
        content="test content",
        description="test description",
    )
    created_layout = await service.create(user, layout_create)

    # 레이아웃 삭제
    await service.delete(user, created_layout.name)

    # 삭제 확인
    with pytest.raises(LayoutNotFoundError):
        await service.get(created_layout.name)


@pytest.mark.asyncio
async def test_layout_service_not_found(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """존재하지 않는 레이아웃 조회 테스트"""
    service = get_temp_env_service(version_info, temp_env)
    with pytest.raises(LayoutNotFoundError):
        await service.get("non_existent_layout")


@pytest.mark.asyncio
async def test_layout_service_invalid_name(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """잘못된 레이아웃 이름 테스트"""
    service = get_temp_env_service(version_info, temp_env)
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
            await service.create(
                user,
                LayoutCreate(
                    name=invalid_name,
                    content="test content",
                    description="test description",
                ),
            )


@pytest.mark.asyncio
async def test_layout_service_update_blocks(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """레이아웃 업데이트 시 블록 변경 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))

    # 기본 레이아웃 생성
    layout = await layout_service.create(
        user,
        LayoutCreate(
            name="test_layout",
            content="""
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
            """,
            description="test layout with blocks",
        ),
    )

    # 블록 변경
    updated_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{% block title %}{% endblock %}</title>
        <meta charset="utf-8">
    </head>
    <body>
        <nav>{% block nav %}{% endblock %}</nav>
        <header>{% block header %}{% endblock %}</header>
        <main>{% block content %}{% endblock %}</main>
        <aside>{% block sidebar %}{% endblock %}</aside>
        <footer>{% block footer %}{% endblock %}</footer>
    </body>
    </html>
    """
    updated_layout, _ = await layout_service.update(
        user,
        layout.name,
        LayoutUpdate(
            content=updated_content,
            description=layout.description,
        ),
    )

    assert "{% block nav %}" in updated_layout.content
    assert "{% block sidebar %}" in updated_layout.content
    assert "{% block title %}" in updated_layout.content
    assert "{% block header %}" in updated_layout.content
    assert "{% block content %}" in updated_layout.content
    assert "{% block footer %}" in updated_layout.content


@pytest.mark.asyncio
async def test_layout_service_multiple(version_info: VersionInfo, temp_env: TemplyEnv, user: User):
    """여러 레이아웃 생성/조회 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))
    layouts = []

    # 여러 레이아웃 생성
    for i in range(3):
        layout = await layout_service.create(
            user,
            LayoutCreate(
                name=f"test_layout_{i}",
                content=f"test layout content {i}",
                description=f"test layout description {i}",
            ),
        )
        layouts.append(layout)

    # 생성된 레이아웃 검증
    for i, layout in enumerate(layouts):
        get_layout = await layout_service.get(layout.name)
        assert get_layout.name == f"test_layout_{i}"
        assert get_layout.content == f"test layout content {i}"
        assert get_layout.description == f"test layout description {i}"
        assert get_layout.created_at is not None
        assert get_layout.created_by == user.name
        assert get_layout.updated_at is not None
        assert get_layout.updated_by == user.name


@pytest.mark.asyncio
async def test_layout_service_inheritance(
    version_info: VersionInfo, temp_env: TemplyEnv, user: User
):
    """레이아웃 상속 관계 테스트"""
    layout_service = LayoutService(LayoutRepository(version_info, temp_env))

    # 기본 레이아웃 생성
    base_layout = await layout_service.create(
        user,
        LayoutCreate(
            name="base_layout",
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{% block title %}{% endblock %}</title>
            </head>
            <body>
                <main>{% block content %}{% endblock %}</main>
            </body>
            </html>
            """,
            description="base layout",
        ),
    )

    # 상속받는 레이아웃 생성
    child_layout = await layout_service.create(
        user,
        LayoutCreate(
            name="child_layout",
            content="""
            {% extends 'layouts/base_layout' %}
            {% block title %}Child Title{% endblock %}
            {% block content %}Child Content{% endblock %}
            """,
            description="child layout",
        ),
    )

    # 상속 관계 검증
    get_child = await layout_service.get(child_layout.name)
    assert "{% extends 'layouts/base_layout' %}" in get_child.content
    assert "{% block title %}Child Title{% endblock %}" in get_child.content
    assert "{% block content %}Child Content{% endblock %}" in get_child.content
