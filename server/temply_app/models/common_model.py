"""
공통 모델
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from temply_app.core.config import Config


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


class VersionInfo:
    """버전 정보 모델"""

    version: str
    main_name: str
    revision_version: str
    pr_number: Optional[str] = None
    is_root: bool = True

    def __init__(
        self,
        config: Config,
        version: str,
    ):
        self.version = version
        self.main_name = config.noti_temply_main_version_name
        self.revision_version = self.version
        self.pr_number = None
        self.is_root = self.version == self.main_name

        # 메인 버전이 아닌 경우에만 버전 형식 검증
        if self.version != self.main_name:
            # 버전 형식이 맞지 않는 경우에도 기본값으로 설정
            if not version_pattern.match(self.version):
                self.revision_version = self.version
                self.pr_number = None
            else:
                parts = self.version.split("_pr")
                self.revision_version = parts[0]
                self.pr_number = f"pr{parts[1]}" if len(parts) > 1 else None

    @classmethod
    def root_version(cls, config: Config) -> "VersionInfo":
        """버전 정보 모델 생성"""
        return cls(config=config, version=config.noti_temply_main_version_name)


class ReturnVersionInfo(BaseModel):
    """버전 정보 모델"""

    version: str = Field(..., description="버전")
    is_root: bool = Field(..., description="메인 버전 여부")


class CreateVersionRequest(BaseModel):
    """버전 생성 요청 모델"""

    version: str = Field(..., description="생성할 버전")
