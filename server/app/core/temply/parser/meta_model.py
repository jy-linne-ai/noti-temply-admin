"""Meta model module."""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, List, Optional, Set
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

    #     """메타데이터를 딕셔너리로 변환합니다."""
    #     return {
    #         "description": self.description or "",
    #         "created_at": (
    #             self.created_at.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S")
    #             if self.created_at
    #             else ""
    #         ),
    #         "created_by": self.created_by or "",
    #         "updated_at": (
    #             self.updated_at.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S")
    #             if self.updated_at
    #             else ""
    #         ),
    #         "updated_by": self.updated_by or "",
    #     }

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

    @classmethod
    def get_current_datetime(cls) -> datetime:
        """현재 시간을 반환합니다."""
        return datetime.now(JST)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Any:
        """Create from dictionary"""
        return cls(**data)


@dataclass
class LayoutMetaData(BaseMetaData):
    """레이아웃 메타데이터를 저장하는 클래스"""

    name: str = ""
    content: str = ""


@dataclass
class PartialMetaData(BaseMetaData):
    """Partial metadata"""

    name: str = ""
    content: str = ""
    dependencies: Set[str] = None  # type: ignore
    parents: List["PartialMetaData"] = None  # type: ignore
    children: List["PartialMetaData"] = None  # type: ignore

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = set()
        if self.parents is None:
            self.parents = []
        if self.children is None:
            self.children = []


@dataclass
class TemplateComponentMetaData(BaseMetaData):
    """템플릿 메타데이터를 저장하는 클래스"""

    template: str = ""
    component: str = ""
    content: str = ""
    layout: Optional[str] = None
    partials: List[str] = None  # type: ignore

    def __post_init__(self):
        """초기화 후 처리"""
        if self.partials is None:
            self.partials = []
