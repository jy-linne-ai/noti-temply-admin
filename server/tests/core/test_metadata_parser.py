"""메타데이터 파서 테스트"""

from datetime import datetime

import pytest

from temply_app.core.temply.parser.meta_model import JST, BaseMetaData
from temply_app.core.utils import parser_meta_util
from temply_app.models.common_model import Meta


@pytest.mark.asyncio
async def test_meta_data_to_dict():
    """BaseMetaData.to_dict() 테스트"""
    meta = BaseMetaData(
        description="테스트 설명",
        created_at=datetime(2024, 3, 21, 12, 0, 0, tzinfo=JST),
        created_by="user1",
        updated_at=datetime(2024, 3, 22, 12, 0, 0, tzinfo=JST),
        updated_by="user2",
    )

    result = Meta.model_validate(meta.to_dict())
    assert result.description == meta.description
    assert result.created_at == meta.created_at
    assert result.created_by == meta.created_by
    assert result.updated_at == meta.updated_at
    assert result.updated_by == meta.updated_by


@pytest.mark.asyncio
async def test_meta_data_to_dict_partial():
    """일부 필드만 있는 BaseMetaData의 to_dict() 테스트"""
    meta = BaseMetaData(
        description="테스트 설명",
        created_at=datetime(2024, 3, 21, 12, 0, 0, tzinfo=JST),
    )

    result = Meta.model_validate(meta.to_dict())
    assert result.description == "테스트 설명"
    assert result.created_at == datetime(2024, 3, 21, 12, 0, 0, tzinfo=JST)
    assert result.created_by is None
    assert result.updated_at is None
    assert result.updated_by is None


@pytest.mark.asyncio
async def test_meta_data_to_jinja_comment(temp_env):
    """BaseMetaData.to_jinja_comment() 테스트"""
    meta = BaseMetaData(
        description="테스트 설명",
        created_at=datetime(2024, 3, 21, 12, 0, 0, tzinfo=JST),
        created_by="user1",
        updated_at=datetime(2024, 3, 22, 12, 0, 0, tzinfo=JST),
        updated_by="user2",
    )
    expected = """{#-
description: 테스트 설명
created_at: 2024-03-21 12:00:00
created_by: user1
updated_at: 2024-03-22 12:00:00
updated_by: user2
-#}"""
    assert temp_env.format_meta_block(meta) == expected


@pytest.mark.asyncio
async def test_meta_data_to_jinja_comment_empty(temp_env):
    """빈 BaseMetaData의 to_jinja_comment() 테스트"""
    meta = BaseMetaData()
    expected = """{#-
description: 
created_at: 
created_by: 
updated_at: 
updated_by: 
-#}"""
    assert temp_env.format_meta_block(meta) == expected


@pytest.mark.asyncio
async def test_meta_data_to_jinja_comment_partial(temp_env):
    """일부 필드만 있는 BaseMetaData의 to_jinja_comment() 테스트"""
    meta = BaseMetaData(
        description="테스트 설명",
        created_at=datetime(2024, 3, 21, 12, 0, 0, tzinfo=JST),
    )

    expected = """{#-
description: 테스트 설명
created_at: 2024-03-21 12:00:00
created_by: 
updated_at: 
updated_by: 
-#}"""
    assert temp_env.format_meta_block(meta) == expected


@pytest.mark.asyncio
async def test_meta_parser_parse():
    """MetaParser.parse_from_file() 테스트"""
    content = """{#-
description:  테스트 설명  
created_at: 2024-03-21 12:00:00
created_by:  user1  
updated_at: 2024-03-22 12:00:00
updated_by:  user2  
-#}
Content"""

    meta, block = parser_meta_util.parse(content)

    assert meta.description == "테스트 설명"
    assert meta.created_at == datetime(2024, 3, 21, 12, 0, 0, tzinfo=JST)
    assert meta.created_by == "user1"
    assert meta.updated_at == datetime(2024, 3, 22, 12, 0, 0, tzinfo=JST)
    assert meta.updated_by == "user2"
    assert block == "Content"


@pytest.mark.asyncio
async def test_meta_parser_parse_date_only():
    """날짜만 있는 메타데이터 파싱 테스트"""
    content = """{#-
description:  테스트 설명  
created_at: 2024-03-21
created_by:  user1  
updated_at: 2024-03-22
updated_by:  user2  
-#}
Content"""

    meta, block = parser_meta_util.parse(content)

    assert meta.description == "테스트 설명"
    assert meta.created_at == datetime(2024, 3, 21, tzinfo=JST)
    assert meta.created_by == "user1"
    assert meta.updated_at == datetime(2024, 3, 22, tzinfo=JST)
    assert meta.updated_by == "user2"
    assert block == "Content"


@pytest.mark.asyncio
async def test_meta_parser_parse_empty():
    """메타데이터가 없는 파일 파싱 테스트"""
    content = "Content"

    meta, block = parser_meta_util.parse(content)

    assert meta.description is None
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None
    assert block == "Content"


@pytest.mark.asyncio
async def test_meta_parser_parse_invalid():
    """잘못된 형식의 메타데이터 파싱 테스트"""
    content = """{#-
invalid line
description:  테스트 설명  
-#}
Content"""

    meta, block = parser_meta_util.parse(content)

    assert meta.description == "테스트 설명"
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None
    assert block == "Content"


@pytest.mark.asyncio
async def test_meta_parser_parse_empty_values():
    """빈 값이 있는 메타데이터 파싱 테스트"""
    content = """{#-
description:  
created_at: 
created_by:  
updated_at: 
updated_by:  
-#}
Content"""

    meta, block = parser_meta_util.parse(content)

    assert meta.description is None
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None
    assert block == "Content"


@pytest.mark.asyncio
async def test_parse_meta_from_content():
    """메타데이터 파싱 테스트"""
    # 테스트용 메타데이터 블록
    content = """{#-
description: 테스트 템플릿
created_at: 2024-07-01
created_by: test_user
updated_at: 2024-07-02
updated_by: test_user
-#}
템플릿 내용"""

    # 메타데이터 파싱
    meta, block = parser_meta_util.parse(content)

    # 메타데이터 검증
    assert meta.description == "테스트 템플릿"
    assert meta.created_at == datetime(2024, 7, 1, tzinfo=JST)
    assert meta.created_by == "test_user"
    assert meta.updated_at == datetime(2024, 7, 2, tzinfo=JST)
    assert meta.updated_by == "test_user"
    assert block == "템플릿 내용"


@pytest.mark.asyncio
async def test_parse_meta_from_content_without_meta():
    """메타데이터가 없는 경우 테스트"""
    content = "템플릿 내용"
    meta, block = parser_meta_util.parse(content)

    # 기본값 검증
    assert meta.description is None
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None
    assert block == "템플릿 내용"


@pytest.mark.asyncio
async def test_parse_meta_from_content_with_invalid_meta():
    """잘못된 메타데이터 형식 테스트"""
    content = """{#-
invalid_key: value
-#}
템플릿 내용"""

    meta, block = parser_meta_util.parse(content)

    # 잘못된 키는 무시되고 기본값 유지
    assert meta.description is None
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None
    assert block == "템플릿 내용"
