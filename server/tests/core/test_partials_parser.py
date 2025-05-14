"""파셜 파서 테스트"""

from datetime import datetime
from pathlib import Path

import pytest
import pytest_asyncio

from app.core.temply.metadata.meta_model import JST
from app.core.temply.metadata.partial_parser import PartialParser


def get_base_path() -> Path:
    """테스트 데이터 경로"""
    base = Path(__file__).parent.parent / "data"
    return base


@pytest.mark.asyncio
async def test_partial_parser():
    """파셜 파서 테스트"""
    base_path = get_base_path()
    parser = PartialParser(base_path / "partials")

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


@pytest_asyncio.fixture
async def parser():
    """PartialParser 인스턴스를 생성하는 fixture"""
    base_path = get_base_path()
    _parser = PartialParser(base_path / "partials")
    # pylint: disable=protected-access
    await _parser._ensure_initialized()  # 초기화 완료 대기
    yield _parser  # return 대신 yield 사용


async def get_temp_parser(tmp_path):
    """Create a parser instance for testing."""
    return PartialParser(tmp_path)


@pytest.mark.asyncio
async def test_get_partial_files(tmp_path):
    """Test getting list of partial files with meta info."""
    # 테스트용 파일 생성
    test_file = tmp_path / "partials_test"
    test_file.write_text("""{#-\ndescription: 파셜 테스트\ncreated_at: 2024-07-01\n-#}\nContent""")
    tmp_parser = await get_temp_parser(tmp_path)
    files = await tmp_parser.get_partials()
    assert len(files) == 1
    assert files[0].name == "partials_test"
    assert files[0].description == "파셜 테스트"
    assert files[0].created_at == datetime(2024, 7, 1, tzinfo=JST)


@pytest.mark.asyncio
async def test_parse_partial(parser):
    """파셜 템플릿 파싱 테스트"""
    dependencies = await parser.get_partial("partials_1")
    assert dependencies is not None


@pytest.mark.asyncio
async def test_build_tree(parser):
    """Test building the dependency tree."""
    tree = await parser.get_partials()

    # Check that all nodes have the correct dependencies
    for node in tree:
        for dependency in node.dependencies:
            partial = await parser.get_partial(dependency)
            assert partial is not None, f"Dependency {dependency} not found in tree"


@pytest.mark.asyncio
async def test_print_tree(parser, capsys):
    """Test printing the dependency tree."""
    await parser.print_tree()
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert "└─" in captured.out


@pytest.mark.asyncio
async def test_get_all_nodes(parser):
    """Test getting all nodes from the tree."""
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
async def test_partials_3_dependencies(parser):
    """Test partials_3 dependencies."""
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


@pytest.mark.asyncio
async def test_partials_53_dependencies(parser):
    """Test partials_53 dependencies."""
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
