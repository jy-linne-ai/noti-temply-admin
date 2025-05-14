"""Meta parser module.

This module provides functionality to parse Jinja2 meta comments.
"""

import re

from app.core.temply.metadata.meta_model import BaseMetaData


def parse_meta_from_content(content: str) -> BaseMetaData:
    """내용에서 메타데이터를 파싱합니다."""
    # 메타데이터 블록 찾기
    pattern = r"^{#-\s*([\s\S]*?)\s*-#}"
    match = re.search(pattern, content)
    if not match:
        return BaseMetaData()

    # 메타데이터 파싱
    meta_dict = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        # 빈 값은 None으로 처리
        meta_dict[key] = None if not value else value

    # BaseMetaData 객체 생성
    return BaseMetaData(
        description=meta_dict.get("description"),
        created_at=BaseMetaData.parse_datetime(meta_dict.get("created_at")),
        created_by=meta_dict.get("created_by"),
        updated_at=BaseMetaData.parse_datetime(meta_dict.get("updated_at")),
        updated_by=meta_dict.get("updated_by"),
    )
