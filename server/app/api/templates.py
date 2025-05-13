from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from jinja2 import Environment
import re
from datetime import datetime

from ..services.template import TemplateService

router = APIRouter(prefix="/api/templates", tags=["templates"])
template_service = TemplateService()

class TemplateRequest(BaseModel):
    content: str

class TemplateResponse(BaseModel):
    rendered: str
    variables: List[str]
    sampleData: Dict[str, Any]

@router.get("/", response_model=List[Dict])
async def list_templates():
    """템플릿 목록을 조회합니다."""
    try:
        return template_service.list_templates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{template_id}", response_model=Dict)
async def get_template(template_id: str):
    """템플릿 정보를 조회합니다."""
    try:
        return template_service.get_template(template_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Dict)
async def create_template(template: Dict):
    """새로운 템플릿을 생성합니다."""
    try:
        # 현재 시간을 메타데이터로 추가
        template["created_at"] = datetime.now().isoformat()
        template["updated_at"] = datetime.now().isoformat()
        return template_service.create_template(template)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{template_id}", response_model=Dict)
async def update_template(template_id: str, template: Dict):
    """템플릿을 수정합니다."""
    try:
        # 수정 시간 업데이트
        template["updated_at"] = datetime.now().isoformat()
        return template_service.update_template(template_id, template)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """템플릿을 삭제합니다."""
    try:
        template_service.delete_template(template_id)
        return {"message": "템플릿이 삭제되었습니다."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_variables(content: str) -> List[str]:
    """템플릿에서 사용된 변수를 추출합니다."""
    variables = set()
    
    # {{ variable }} 패턴 찾기
    expression_pattern = r'{{([^}]+)}}'
    for match in re.finditer(expression_pattern, content):
        expr = match.group(1).strip()
        # 필터 제거하고 변수만 추출
        var_name = expr.split('|')[0].strip()
        if var_name and not var_name.startswith(('if', 'for')):
            variables.add(var_name)

    # {% if variable %} 패턴 찾기
    block_pattern = r'{%\s*(if|elif|for)\s+([^%]+)%}'
    for match in re.finditer(block_pattern, content):
        expr = match.group(2).strip()
        # 조건문에서 변수 추출
        vars = re.split(r'\s+(and|or|in)\s+', expr)
        for var in vars:
            var_name = var.strip()
            if var_name and not var_name.startswith(('if', 'for')):
                variables.add(var_name)

    return list(variables)

def generate_sample_data(variables: List[str]) -> Dict[str, Any]:
    """변수에 대한 샘플 데이터를 생성합니다."""
    sample_data = {
        'title': '샘플 제목',
        'name': '홍길동',
        'email': 'user@example.com',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'price': '10,000원',
        'count': 5,
        'items': ['항목 1', '항목 2', '항목 3'],
        'user': {'name': '홍길동', 'role': '관리자'},
        'is_admin': True,
        'is_active': True,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
    }

    # 실제 사용된 변수에 대해서만 샘플 데이터 필터링
    return {var: sample_data.get(var, '샘플 데이터') for var in variables}

@router.post("/preview", response_model=TemplateResponse)
async def preview_template(request: TemplateRequest):
    try:
        # Jinja2 환경 설정
        env = Environment(
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

        # 템플릿에서 변수 추출
        variables = extract_variables(request.content)
        
        # 샘플 데이터 생성
        sample_data = generate_sample_data(variables)
        
        # 템플릿 렌더링
        template = env.from_string(request.content)
        rendered = template.render(**sample_data)

        return TemplateResponse(
            rendered=rendered,
            variables=variables,
            sampleData=sample_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"템플릿 렌더링 중 오류 발생: {str(e)}"
        ) 