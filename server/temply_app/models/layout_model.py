from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from temply_app.models.common_model import Meta


class LayoutCreate(BaseModel):
    """레이아웃 생성 모델"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="레이아웃 이름")
    description: Optional[str] = Field(None, description="레이아웃 설명")
    content: str = Field(..., description="레이아웃 HTML 내용")


class LayoutUpdate(BaseModel):
    """레이아웃 수정 모델"""

    model_config = ConfigDict(from_attributes=True)
    description: Optional[str] = Field(None, description="레이아웃 설명")
    content: str = Field(..., description="레이아웃 HTML 내용")


class Layout(Meta):
    """레이아웃 모델"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="레이아웃 이름")
    content: str = Field(..., description="레이아웃 HTML 내용")


class LayoutUpdateResponse(Layout):
    """레이아웃 수정 응답 모델"""

    model_config = ConfigDict(from_attributes=True)

    updated_template_files: List[str] = Field([], description="수정된 템플릿 파일 목록")
