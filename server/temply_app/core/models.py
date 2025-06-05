"""
데이터 모델을 관리하는 모듈
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CategoryType(str, Enum):
    """카테고리 타입"""

    TEMPLATE = "templates"
    LAYOUT = "layouts"
    PARTIAL = "partials"


class CategoryInfo(BaseModel):
    """카테고리 정보를 담는 모델"""

    category_type: CategoryType
    name: str
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None


class ItemType(str, Enum):
    """아이템 타입"""

    CONTENT = "content"
    SCHEMA = "schema"
    METADATA = "metadata"


class ItemInfo(BaseModel):
    """아이템 정보를 담는 모델"""

    item_type: ItemType
    updated_at: str
    content: str
