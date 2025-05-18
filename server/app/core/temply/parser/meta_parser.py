"""Meta parser module.

This module provides functionality to parse Jinja2 meta comments.
"""

import re

from app.core.temply.parser.meta_model import BaseMetaData


class MetaParser:
    """Meta parser class."""

    @staticmethod
    def parse(content: str) -> tuple[BaseMetaData, str]:
        """파일의 시작 부분에 있는 메타데이터 블록을 파싱하고 제거합니다.

        Args:
            content (str): 파싱할 전체 내용

        Returns:
            tuple[BaseMetaData, str]: (파싱된 메타데이터, 메타데이터 블록이 제거된 나머지 내용)
        """
        block = content
        # 메타데이터 블록 찾기
        pattern = r"^{#-\s*([\s\S]*?)\s*-#}"
        match = re.search(pattern, block)
        if not match:
            return BaseMetaData(), block

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
        if match:
            # 메타데이터 블록 이후의 내용만 사용
            block = block[match.end() :].lstrip()

        return (
            BaseMetaData(
                description=meta_dict.get("description"),
                created_at=BaseMetaData.parse_datetime(meta_dict.get("created_at")),
                created_by=meta_dict.get("created_by"),
                updated_at=BaseMetaData.parse_datetime(meta_dict.get("updated_at")),
                updated_by=meta_dict.get("updated_by"),
            ),
            block,
        )
