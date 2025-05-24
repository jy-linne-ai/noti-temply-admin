"""파셜 모델"""

from typing import Optional, Set

from pydantic import BaseModel, ConfigDict, Field

from app.models.common_model import Meta


class PartialCreate(BaseModel):
    """파셜 생성 모델"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="파셜 이름")
    description: Optional[str] = Field(None, description="파셜 설명")
    dependencies: Set[str] = Field(..., description="파셜 의존성")
    content: str = Field(..., description="파셜 HTML 내용")


class PartialUpdate(BaseModel):
    """파셜 수정 모델"""

    model_config = ConfigDict(from_attributes=True)

    description: Optional[str] = Field(None, description="파셜 설명")
    dependencies: Set[str] = Field(..., description="파셜 의존성")
    content: str = Field(..., description="파셜 HTML 내용")


class Partial(Meta):
    """파셜 모델"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="파셜 이름")
    dependencies: Set[str] = Field(..., description="파셜 의존성")
    content: str = Field(..., description="파셜 HTML 내용")
