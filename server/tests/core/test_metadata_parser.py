"""메타데이터 파서 테스트"""

from datetime import datetime

import pytest

from app.core.temply.metadata.meta_model import JST, BaseMetaData
from app.core.temply.metadata.meta_parser import parse_meta_from_content


@pytest.mark.asyncio
def test_meta_data_to_dict():
    """BaseMetaData.to_dict() 테스트"""
    meta = BaseMetaData(
        description="테스트 설명",
        created_at=datetime(2024, 3, 21, 12, 0, 0, tzinfo=JST),
        created_by="user1",
        updated_at=datetime(2024, 3, 22, 12, 0, 0, tzinfo=JST),
        updated_by="user2",
    )

    result = meta.to_dict()
    assert result["description"] == "테스트 설명"
    assert result["created_at"] == "2024-03-21 12:00:00"
    assert result["created_by"] == "user1"
    assert result["updated_at"] == "2024-03-22 12:00:00"
    assert result["updated_by"] == "user2"


@pytest.mark.asyncio
def test_meta_data_to_dict_partial():
    """일부 필드만 있는 BaseMetaData의 to_dict() 테스트"""
    meta = BaseMetaData(
        description="테스트 설명",
        created_at=datetime(2024, 3, 21, 12, 0, 0, tzinfo=JST),
    )

    result = meta.to_dict()
    assert result["description"] == "테스트 설명"
    assert result["created_at"] == "2024-03-21 12:00:00"
    assert result["created_by"] == ""
    assert result["updated_at"] == ""
    assert result["updated_by"] == ""


@pytest.mark.asyncio
def test_meta_data_to_jinja_comment():
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
    assert meta.to_jinja_comment() == expected


@pytest.mark.asyncio
def test_meta_data_to_jinja_comment_empty():
    """빈 BaseMetaData의 to_jinja_comment() 테스트"""
    meta = BaseMetaData()
    expected = """{#-
description: 
created_at: 
created_by: 
updated_at: 
updated_by: 
-#}"""
    assert meta.to_jinja_comment() == expected


@pytest.mark.asyncio
def test_meta_data_to_jinja_comment_partial():
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
    assert meta.to_jinja_comment() == expected


@pytest.mark.asyncio
def test_meta_parser_parse():
    """MetaParser.parse_from_file() 테스트"""
    content = """{#-
description:  테스트 설명  
created_at: 2024-03-21 12:00:00
created_by:  user1  
updated_at: 2024-03-22 12:00:00
updated_by:  user2  
-#}
Content"""

    meta = parse_meta_from_content(content)

    assert meta.description == "테스트 설명"
    assert meta.created_at == datetime(2024, 3, 21, 12, 0, 0, tzinfo=JST)
    assert meta.created_by == "user1"
    assert meta.updated_at == datetime(2024, 3, 22, 12, 0, 0, tzinfo=JST)
    assert meta.updated_by == "user2"


@pytest.mark.asyncio
def test_meta_parser_parse_date_only():
    """날짜만 있는 메타데이터 파싱 테스트"""
    content = """{#-
description:  테스트 설명  
created_at: 2024-03-21
created_by:  user1  
updated_at: 2024-03-22
updated_by:  user2  
-#}
Content"""

    meta = parse_meta_from_content(content)

    assert meta.description == "테스트 설명"
    assert meta.created_at == datetime(2024, 3, 21, tzinfo=JST)
    assert meta.created_by == "user1"
    assert meta.updated_at == datetime(2024, 3, 22, tzinfo=JST)
    assert meta.updated_by == "user2"


@pytest.mark.asyncio
def test_meta_parser_parse_empty(tmp_path):
    """메타데이터가 없는 파일 파싱 테스트"""
    content = "Content"

    meta = parse_meta_from_content(content)

    assert meta.description is None
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None


@pytest.mark.asyncio
def test_meta_parser_parse_invalid(tmp_path):
    """잘못된 형식의 메타데이터 파싱 테스트"""
    content = """{#-
invalid line
description:  테스트 설명  
-#}
Content"""

    meta = parse_meta_from_content(content)

    assert meta.description == "테스트 설명"
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None


@pytest.mark.asyncio
def test_meta_parser_parse_empty_values(tmp_path):
    """빈 값이 있는 메타데이터 파싱 테스트"""
    content = """{#-
description:  
created_at: 
created_by:  
updated_at: 
updated_by:  
-#}
Content"""

    meta = parse_meta_from_content(content)

    assert meta.description is None
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None


@pytest.mark.asyncio
def test_parse_meta_from_content():
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
    meta = parse_meta_from_content(content)

    # 메타데이터 검증
    assert meta.description == "테스트 템플릿"
    assert meta.created_at == datetime(2024, 7, 1, tzinfo=JST)
    assert meta.created_by == "test_user"
    assert meta.updated_at == datetime(2024, 7, 2, tzinfo=JST)
    assert meta.updated_by == "test_user"


@pytest.mark.asyncio
def test_parse_meta_from_content_without_meta():
    """메타데이터가 없는 경우 테스트"""
    content = "템플릿 내용"
    meta = parse_meta_from_content(content)

    # 기본값 검증
    assert meta.description is None
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None


@pytest.mark.asyncio
def test_parse_meta_from_content_with_invalid_meta():
    """잘못된 메타데이터 형식 테스트"""
    content = """{#-
invalid_key: value
-#}
템플릿 내용"""

    meta = parse_meta_from_content(content)

    # 잘못된 키는 무시되고 기본값 유지
    assert meta.description is None
    assert meta.created_at is None
    assert meta.created_by is None
    assert meta.updated_at is None
    assert meta.updated_by is None
