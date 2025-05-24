"""템플릿 모델"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.common_model import Meta


class TemplateComponentCreate(BaseModel):
    """템플릿 컴포넌트 생성 모델"""

    model_config = ConfigDict(from_attributes=True)

    # template: str = Field(..., description="템플릿 카테고리")
    component: str = Field(..., description="템플릿 컴포넌트")
    description: Optional[str] = Field(None, description="템플릿 설명")
    layout: Optional[str] = Field(None, description="템플릿 레이아웃")
    partials: Optional[List[str]] = Field(None, description="템플릿 파셜")
    content: str = Field(..., description="템플릿 내용")


class TemplateComponentUpdate(BaseModel):
    """템플릿 수정 모델"""

    model_config = ConfigDict(from_attributes=True)

    description: Optional[str] = Field(None, description="템플릿 설명")
    layout: Optional[str] = Field(None, description="템플릿 레이아웃")
    partials: Optional[List[str]] = Field(None, description="템플릿 파셜")
    content: str = Field(..., description="템플릿 내용")


class TemplateComponent(Meta):
    """템플릿 컴포넌트 모델"""

    model_config = ConfigDict(from_attributes=True)

    template: str = Field(..., description="템플릿 카테고리")
    component: str = Field(..., description="템플릿 컴포넌트")
    layout: Optional[str] = Field(None, description="템플릿 레이아웃")
    partials: Optional[List[str]] = Field(None, description="템플릿 파셜")
    content: str = Field(..., description="템플릿 내용")
