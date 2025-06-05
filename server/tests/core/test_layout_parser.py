"""레이아웃 파서 테스트"""

import pytest

from temply_app.core.temply.parser.layout_parser import LayoutParser


@pytest.mark.asyncio
async def test_layout_parser(data_env):
    """레이아웃 파서 테스트"""
    parser = LayoutParser(data_env)

    # 레이아웃 파일 파싱
    layouts = await parser.get_layouts()
    assert len(layouts) > 0

    # 레이아웃 트리 출력
    await parser.print_layout_tree()
