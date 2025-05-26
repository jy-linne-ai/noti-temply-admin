"""
공통 모델
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.config import Config


class User(BaseModel):
    """사용자 모델"""

    name: str


class Meta(BaseModel):
    """메타데이터 모델"""

    description: Optional[str] = Field(None, description="설명")
    created_at: Optional[datetime] = Field(None, description="생성 시간")
    created_by: Optional[str] = Field(None, description="생성자")
    updated_at: Optional[datetime] = Field(None, description="수정 시간")
    updated_by: Optional[str] = Field(None, description="수정자")


version_pattern = re.compile(r"^r\d+(?:_pr\d+)?$")


class VersionInfo(BaseModel):
    """버전 정보 모델"""

    version: str = Field(..., description="버전")
    main_name: str = Field("main", description="메인 버전 이름")
    revision_version: Optional[str] = Field(None, description="리비전 버전")
    pr_number: Optional[str] = Field(None, description="PR 번호")
    config: Config = Field(..., description="설정")

    def __init__(self, config: Config, version: str) -> None:
        super().__init__(
            version=version, main_name=config.noti_temply_main_version_name, config=config
        )
        self.__post_init__()

    @property
    def is_root(self) -> bool:
        """메인 버전인지 여부를 반환합니다."""
        # pylint: disable=no-member
        return self.version == self.config.noti_temply_main_version_name

    def __post_init__(self) -> None:
        assert self.main_name is not None
        self.version = self.version.strip()
        self.revision_version = self.version
        if self.version != self.main_name:
            if not version_pattern.match(self.version):
                raise ValueError("Invalid version format")

            # 버전이 검증된 후에 분리
            parts = self.version.split("_pr")
            self.revision_version = parts[0]
            self.pr_number = f"pr{parts[1]}" if len(parts) > 1 else None

    @classmethod
    def root_version(cls, config: Config) -> "VersionInfo":
        """버전 정보 모델 생성"""
        return cls(config, config.noti_temply_main_version_name)
