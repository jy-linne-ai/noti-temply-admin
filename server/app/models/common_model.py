"""
공통 모델
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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


class VersionInfo(BaseModel):
    version: str
    is_root: bool = False
