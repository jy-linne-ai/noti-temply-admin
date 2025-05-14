"""레이아웃 파서 테스트"""

from pathlib import Path

import pytest

from app.core.temply.metadata.layout_parser import LayoutParser


def get_base_path() -> Path:
    """테스트 데이터 경로"""
    base = Path(__file__).parent.parent / "data"
    return base


@pytest.mark.asyncio
async def test_layout_parser():
    """레이아웃 파서 테스트"""
    base_path = get_base_path()
    parser = LayoutParser(base_path / "layouts")

    # 레이아웃 파일 파싱
    layouts = await parser.get_layouts()
    assert len(layouts) > 0

    # 레이아웃 트리 출력
    await parser.print_layout_tree()
