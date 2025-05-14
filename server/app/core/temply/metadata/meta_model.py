"""Meta model module."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set
from zoneinfo import ZoneInfo

# JST 타임존 상수
JST = ZoneInfo("Asia/Tokyo")


@dataclass
class BaseMetaData:
    """기본 메타데이터를 저장하는 클래스"""

    description: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """메타데이터를 딕셔너리로 변환합니다."""
        return {
            "description": self.description or "",
            "created_at": (
                self.created_at.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S")
                if self.created_at
                else ""
            ),
            "created_by": self.created_by or "",
            "updated_at": (
                self.updated_at.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S")
                if self.updated_at
                else ""
            ),
            "updated_by": self.updated_by or "",
        }

    def to_jinja_comment(self) -> str:
        """메타데이터를 Jinja2 주석 형식으로 변환합니다."""
        lines = ["{#-"]

        lines.append(f"description: {self.description or ''}")
        lines.append(
            # pylint: disable=line-too-long
            f"created_at: {self.created_at.astimezone(JST).strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''}"
        )
        lines.append(f"created_by: {self.created_by or ''}")
        lines.append(
            # pylint: disable=line-too-long
            f"updated_at: {self.updated_at.astimezone(JST).strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''}"
        )
        lines.append(f"updated_by: {self.updated_by or ''}")
        lines.append("-#}")
        return "\n".join(lines)

    @classmethod
    def parse_datetime(cls, value: Optional[str]) -> Optional[datetime]:
        """날짜 문자열을 datetime 객체로 변환합니다."""
        if not value:
            return None

        formats = [
            "%Y-%m-%d %H:%M:%S",  # 2024-07-01 12:34:56
            "%Y-%m-%d",  # 2024-07-01
            "%Y/%m/%d %H:%M:%S",  # 2024/07/01 12:34:56
            "%Y/%m/%d",  # 2024/07/01
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.replace(tzinfo=JST)
            except ValueError:
                continue

        return None


@dataclass
class LayoutMetaData(BaseMetaData):
    """레이아웃 메타데이터를 저장하는 클래스"""

    name: str = ""
    content: str = ""

    def to_dict(self) -> Dict[str, str]:
        """메타데이터를 딕셔너리로 변환합니다."""
        result = super().to_dict()
        if self.name:
            result["name"] = self.name
        if self.content:
            result["content"] = self.content
        return result


@dataclass
class PartialMetaData(BaseMetaData):
    """파셜 메타데이터를 저장하는 클래스"""

    name: str = ""
    content: str = ""
    dependencies: Set[str] = None  # type: ignore
    children: List["PartialMetaData"] = None  # type: ignore
    parents: List["PartialMetaData"] = None  # type: ignore

    def __post_init__(self):
        """초기화 후 처리"""
        if self.dependencies is None:
            self.dependencies = set()
        if self.children is None:
            self.children = []
        if self.parents is None:
            self.parents = []

    def to_dict(self) -> Dict[str, str]:
        """메타데이터를 딕셔너리로 변환합니다."""
        result = super().to_dict()
        if self.name:
            result["name"] = self.name
        if self.content:
            result["content"] = self.content
        return result


@dataclass
class TemplateMetaData(BaseMetaData):
    """템플릿 메타데이터를 저장하는 클래스"""

    category: str = ""
    name: str = ""
    content: str = ""
    layout: Optional[str] = None
    partials: List[str] = None  # type: ignore

    def __post_init__(self):
        """초기화 후 처리"""
        if self.partials is None:
            self.partials = []

    def to_dict(self) -> Dict[str, str]:
        """메타데이터를 딕셔너리로 변환합니다."""
        result = super().to_dict()
        if self.category:
            result["category"] = self.category
        if self.name:
            result["name"] = self.name
        if self.content:
            result["content"] = self.content
        if self.layout:
            result["layout"] = self.layout
        if self.partials:
            result["partials"] = ",".join(sorted(self.partials))
        return result
