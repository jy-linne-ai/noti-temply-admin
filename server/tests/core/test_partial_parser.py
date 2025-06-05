"""파셜 파서 테스트"""

from datetime import datetime

import pytest

from temply_app.core.exceptions import (
    PartialAlreadyExistsError,
    PartialCircularDependencyError,
    PartialNotFoundError,
)
from temply_app.core.temply.parser.meta_model import JST, BaseMetaData, PartialMetaData
from temply_app.core.temply.parser.partial_parser import PartialParser
from temply_app.models.common_model import User


@pytest.mark.asyncio
async def test_partial_parser(data_env):
    """파셜 파서 테스트"""
    parser = PartialParser(data_env)

    # 파셜 파일 파싱
    partials = await parser.get_partials()
    assert len(partials) > 0

    # 의존성 트리 구축
    dependency_tree = await parser.get_root_partials()
    assert len(dependency_tree) > 0

    # 각 노드의 parents 상태 출력
    for node in dependency_tree:
        print(f"Node: {node.name}, Parents: {node.parents}")

    # 모든 노드의 parents가 None인지 확인
    assert all(not node.parents for node in dependency_tree)

    # 하나라도 children이 있는 노드가 있는지 확인
    assert any(len(node.children) > 0 for node in dependency_tree)

    # 의존성 트리 출력
    await parser.print_dependency_tree()


@pytest.mark.asyncio
async def test_get_partial_files(temp_env):
    """Test getting list of partial files with meta info."""
    # 테스트용 파일 생성
    test_file = temp_env.partials_dir / "partials_test"
    test_file.write_text(
        """{#-\ndescription: 파셜 테스트\ncreated_at: 2024-07-01\n-#}\n{%- macro render() -%}\nContent\n{%- endmacro -%}\n"""
    )
    parser = PartialParser(temp_env)
    files = await parser.get_partials()
    assert len(files) == 1
    assert files[0].name == "partials_test"
    assert files[0].description == "파셜 테스트"
    assert files[0].created_at == datetime(2024, 7, 1, tzinfo=JST)
    assert files[0].dependencies == set()
    assert files[0].children == []
    assert files[0].parents == []
    assert files[0].content == "Content"


@pytest.mark.asyncio
async def test_parse_partial(data_env):
    """파셜 템플릿 파싱 테스트"""
    parser = PartialParser(data_env)
    partial = await parser.get_partial("partials_1")
    assert partial is not None
    assert partial.dependencies == set()
    assert partial.children == []
    assert partial.parents == []


@pytest.mark.asyncio
async def test_build_tree(data_env):
    """Test building the dependency tree."""
    parser = PartialParser(data_env)
    tree = await parser.get_partials()

    # Check that all nodes have the correct dependencies
    for node in tree:
        for dependency in node.dependencies:
            partial = await parser.get_partial(dependency)
            assert partial is not None, f"Dependency {dependency} not found in tree"


@pytest.mark.asyncio
async def test_print_tree(data_env, capsys):
    """Test printing the dependency tree."""
    parser = PartialParser(data_env)
    await parser.print_tree()
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert "└─" in captured.out


@pytest.mark.asyncio
async def test_get_all_nodes(data_env):
    """Test getting all nodes from the tree."""
    parser = PartialParser(data_env)
    all_nodes = await parser.get_partials()

    # 모든 노드가 있는지 확인
    assert len(all_nodes) > 0

    # 노드 이름 목록
    node_names = {node.name for node in all_nodes}

    # 특정 노드들이 있는지 확인
    assert "partials_53" in node_names
    assert "partials_3" in node_names
    assert "partials_31" in node_names

    # 각 노드의 구조가 올바른지 확인
    for node in all_nodes:
        assert isinstance(node.name, str)
        assert isinstance(node.dependencies, set)
        assert isinstance(node.children, list)
        assert isinstance(node.parents, list)


@pytest.mark.asyncio
async def test_partials_3_dependencies(data_env):
    """Test partials_3 dependencies."""
    parser = PartialParser(data_env)
    # partials_3 노드 확인
    node_3 = await parser.get_partial("partials_3")
    assert node_3 is not None, "partials_3 should exist in the tree"

    # partials_3의 자식 노드 확인
    child_names = {child.name for child in node_3.children}
    assert "partials_53" in child_names, "partials_3 should have partials_53 as a child"
    assert "partials_42" in child_names, "partials_3 should have partials_42 as a child"
    assert "partials_43" in child_names, "partials_3 should have partials_43 as a child"
    assert "partials_44" in child_names, "partials_3 should have partials_44 as a child"
    assert "partials_45" in child_names, "partials_3 should have partials_45 as a child"
    assert "partials_46" in child_names, "partials_3 should have partials_46 as a child"
    assert "partials_55" in child_names, "partials_3 should have partials_55 as a child"
    assert len(child_names) == 7, "partials_3 should have exactly 7 children"
    assert len(node_3.dependencies) == 0, "partials_3 should have no dependencies"
    assert node_3.dependencies == set()
    assert node_3.content != ""


@pytest.mark.asyncio
async def test_partials_53_dependencies(data_env):
    """Test partials_53 dependencies."""
    parser = PartialParser(data_env)
    # partials_53 노드 확인
    node_53 = await parser.get_partial("partials_53")
    assert node_53 is not None, "partials_53 should exist in the tree"

    # partials_53의 부모 노드 확인
    parent_names = {parent.name for parent in node_53.parents}
    assert "partials_3" in parent_names, "partials_53 should have partials_3 as a parent"
    assert "partials_31" in parent_names, "partials_53 should have partials_31 as a parent"
    assert len(parent_names) == 2, "partials_53 should have exactly 2 parents"

    # partials_3과 partials_31의 자식으로 partials_53이 있는지 확인
    node_3 = await parser.get_partial("partials_3")
    node_31 = await parser.get_partial("partials_31")

    assert node_3 is not None, "partials_3 should exist in the tree"
    assert node_31 is not None, "partials_31 should exist in the tree"

    child_names_3 = {child.name for child in node_3.children}
    child_names_31 = {child.name for child in node_31.children}

    assert "partials_53" in child_names_3, "partials_3 should have partials_53 as a child"
    assert "partials_53" in child_names_31, "partials_31 should have partials_53 as a child"
    assert node_3.content != ""
    assert node_31.content != ""
    assert node_53.content != ""


@pytest.mark.asyncio
async def test_partial_parser_initialization(temp_env):
    """PartialParser 초기화 테스트"""
    parser = PartialParser(temp_env)
    assert parser.env == temp_env
    assert not parser._initialized


@pytest.mark.asyncio
async def test_partial_parser_parse_partial(temp_env):
    """파셜 파싱 테스트"""
    parser = PartialParser(temp_env)
    # 테스트 파셜 생성
    partial_name = "test_partial"
    partial_path = temp_env.partials_dir / partial_name
    partial_content = (
        temp_env.format_meta_block(
            BaseMetaData(
                description="test partial",
            )
        )
        + "\n"
        + temp_env.format_partial_content("test content")
    )
    partial_path.write_text(partial_content, encoding=temp_env.file_encoding)

    await parser.refresh()
    # 파셜 파싱
    meta = await parser.get_partial(partial_name)
    assert isinstance(meta, PartialMetaData)
    assert meta.name == partial_name
    assert meta.description == "test partial"
    assert meta.content == "test content"


@pytest.mark.asyncio
async def test_partial_parser_build_dependency_tree(temp_env):
    """의존성 트리 구축 테스트"""
    parser = PartialParser(temp_env)

    # 테스트 파셜들 생성
    parent_content = (
        temp_env.format_meta_block(
            BaseMetaData(
                description="parent partial",
            )
        )
        + "\n"
        + temp_env.format_partial_content("parent content")
    )
    child_content = (
        temp_env.format_meta_block(
            BaseMetaData(
                description="child partial",
            )
        )
        + "\n"
        + "\n".join(temp_env.format_partial_imports({"parent_partial"}))
        + "\n"
        + temp_env.format_partial_content("child content")
    )

    parent_path = temp_env.partials_dir / "parent_partial"
    child_path = temp_env.partials_dir / "child_partial"

    parent_path.write_text(parent_content, encoding=temp_env.file_encoding)
    child_path.write_text(child_content, encoding=temp_env.file_encoding)

    # 의존성 트리 구축
    await parser.refresh()

    # 결과 검증
    parent_meta = await parser.get_partial("parent_partial")
    child_meta = await parser.get_partial("child_partial")

    assert "child_partial" in [child.name for child in parent_meta.children]
    assert "parent_partial" in [parent.name for parent in child_meta.parents]


@pytest.mark.asyncio
async def test_partial_parser_circular_dependency(temp_env, user: User):
    """순환 의존성 검사 테스트"""
    parser = PartialParser(temp_env)

    # 두 파셜을 의존성 없이 생성
    await parser.create(
        user,
        "partial1",
        "content 1",
        description="partial 1",
        dependencies=set(),
    )

    await parser.create(
        user,
        "partial2",
        "content 2",
        description="partial 2",
        dependencies=set(),
    )

    # partial2가 partial1에 의존하도록 업데이트
    await parser.update(
        user,
        "partial2",
        "content 2",
        description="partial 2",
        dependencies={"partial1"},
    )

    # partial1이 partial2에 의존하도록 업데이트 시도 (순환 의존성 발생)
    with pytest.raises(
        PartialCircularDependencyError,
        match="Circular dependency detected: partial1 -> partial2 -> partial1",
    ):
        await parser.update(
            user,
            "partial1",
            "content 1",
            description="partial 1",
            dependencies={"partial2"},
        )


@pytest.mark.asyncio
async def test_partial_parser_get_partials(temp_env):
    """파셜 목록 조회 테스트"""
    parser = PartialParser(temp_env)

    # 테스트 파셜들 생성
    partials = ["partial1", "partial2", "partial3"]
    for partial in partials:
        path = temp_env.partials_dir / partial
        path.write_text("test content", encoding=temp_env.file_encoding)

    # 파셜 목록 조회
    partial_list = await parser.get_partials()
    assert len(partial_list) == len(partials)
    assert all(p.name in partials for p in partial_list)


@pytest.mark.asyncio
async def test_partial_parser_get_partial(temp_env):
    """단일 파셜 조회 테스트"""
    parser = PartialParser(temp_env)

    # 테스트 파셜 생성
    partial_name = "test_partial"
    partial_content = """
    {#-
        description: test partial
    -#}
    test content
    """
    partial_path = temp_env.partials_dir / partial_name
    partial_path.write_text(partial_content, encoding=temp_env.file_encoding)

    # 파셜 조회
    partial = await parser.get_partial(partial_name)
    assert partial.name == partial_name
    assert partial.description == "test partial"


@pytest.mark.asyncio
async def test_partial_parser_get_partial_not_found(temp_env):
    """존재하지 않는 파셜 조회 테스트"""
    parser = PartialParser(temp_env)

    with pytest.raises(PartialNotFoundError, match="not found"):
        await parser.get_partial("non_existent_partial")


@pytest.mark.asyncio
async def test_partial_parser_create_partial(temp_env, user: User):
    """파셜 생성 테스트"""
    parser = PartialParser(temp_env)

    # 파셜 생성
    partial_name = "new_partial"
    partial_content = "new content"
    dependencies = {"parent_partial"}

    # 부모 파셜 생성
    parent_path = temp_env.partials_dir / "parent_partial"
    parent_path.write_text("parent content", encoding=temp_env.file_encoding)

    # 새 파셜 생성
    await parser.create(user, partial_name, partial_content, dependencies=dependencies)

    # 생성된 파셜 검증
    partial = await parser.get_partial(partial_name)
    assert partial.name == partial_name
    assert "parent_partial" in partial.dependencies

    # 파일 내용 검증
    partial_path = temp_env.partials_dir / partial_name
    assert partial_path.exists()
    content = partial_path.read_text(encoding=temp_env.file_encoding)
    assert partial_content in content
    assert "parent_partial" in content


@pytest.mark.asyncio
async def test_partial_parser_create_partial_duplicate(temp_env, user: User):
    """중복 파셜 생성 테스트"""
    parser = PartialParser(temp_env)

    # 기존 파셜 생성
    partial_name = "existing_partial"
    partial_path = temp_env.partials_dir / partial_name
    partial_path.write_text("existing content", encoding=temp_env.file_encoding)

    # 중복 생성 시도
    with pytest.raises(PartialAlreadyExistsError, match="already exists"):
        await parser.create(user, partial_name, "new content", dependencies=set())


@pytest.mark.asyncio
async def test_partial_parser_update_partial(temp_env, user: User):
    """파셜 업데이트 테스트"""
    parser = PartialParser(temp_env)

    # 기존 파셜 생성
    partial_name = "test_partial"
    old_content = "old content"
    partial_path = temp_env.partials_dir / partial_name
    partial_path.write_text(old_content, encoding=temp_env.file_encoding)

    # 파셜 업데이트
    new_content = "new content"
    new_dependencies = {"parent_partial"}

    # 부모 파셜 생성
    parent_path = temp_env.partials_dir / "parent_partial"
    parent_path.write_text("parent content", encoding=temp_env.file_encoding)

    # 업데이트
    await parser.update(user, partial_name, new_content, dependencies=new_dependencies)

    # 업데이트된 파셜 검증
    partial = await parser.get_partial(partial_name)
    assert "parent_partial" in partial.dependencies

    # 파일 내용 검증
    content = partial_path.read_text(encoding=temp_env.file_encoding)
    assert new_content in content
    assert "parent_partial" in content


@pytest.mark.asyncio
async def test_partial_parser_update_partial_not_found(temp_env, user: User):
    """존재하지 않는 파셜 업데이트 테스트"""
    parser = PartialParser(temp_env)

    with pytest.raises(PartialNotFoundError, match="not found"):
        await parser.update(user, "non_existent_partial", "new content", dependencies=set())


@pytest.mark.asyncio
async def test_partial_parser_delete_partial(temp_env, user: User):
    """파셜 삭제 테스트"""
    parser = PartialParser(temp_env)

    # 테스트 파셜 생성
    partial_name = "test_partial"
    partial_path = temp_env.partials_dir / partial_name
    partial_path.write_text("test content", encoding=temp_env.file_encoding)

    # 파셜 삭제
    await parser.delete(user, partial_name)

    # 삭제 검증
    assert not partial_path.exists()
    with pytest.raises(PartialNotFoundError, match="not found"):
        await parser.get_partial(partial_name)


@pytest.mark.asyncio
async def test_partial_parser_delete_partial_not_found(temp_env, user: User):
    """존재하지 않는 파셜 삭제 테스트"""
    parser = PartialParser(temp_env)

    with pytest.raises(PartialNotFoundError, match="not found"):
        await parser.delete(user, "non_existent_partial")
