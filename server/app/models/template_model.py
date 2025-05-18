"""템플릿 모델"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.common_model import Meta


class TemplateCreate(BaseModel):
    """템플릿 생성 모델"""

    category: str = Field(..., description="템플릿 카테고리")
    name: str = Field(..., description="템플릿 이름")
    description: Optional[str] = Field(None, description="템플릿 설명")
    layout: Optional[str] = Field(None, description="템플릿 레이아웃")
    partials: Optional[List[str]] = Field(None, description="템플릿 파셜")
    content: str = Field(..., description="템플릿 내용")

    class Config:
        """Config"""

        from_attributes = True


class TemplateUpdate(BaseModel):
    """템플릿 수정 모델"""

    description: Optional[str] = Field(None, description="템플릿 설명")
    layout: Optional[str] = Field(None, description="템플릿 레이아웃")
    partials: Optional[List[str]] = Field(None, description="템플릿 파셜")
    content: str = Field(..., description="템플릿 내용")


class Template(Meta):
    """템플릿 모델"""

    category: str = Field(..., description="템플릿 카테고리")
    name: str = Field(..., description="템플릿 이름")
    layout: Optional[str] = Field(None, description="템플릿 레이아웃")
    partials: Optional[List[str]] = Field(None, description="템플릿 파셜")
    content: str = Field(..., description="템플릿 내용")

    class Config:
        """Config"""

        from_attributes = True
