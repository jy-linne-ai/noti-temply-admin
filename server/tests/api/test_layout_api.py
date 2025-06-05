"""레이아웃 API 테스트"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_get_layouts_empty(client: TestClient):
    """레이아웃 목록이 비어있을 때의 테스트"""
    response = client.get("/api/v1/versions/main/layouts")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_layouts_with_data(client: TestClient, tmp_path):
    """레이아웃 데이터가 있을 때의 테스트"""
    # 테스트 데이터 생성
    test_layout = {
        "name": "TestLayout",
        "description": "Test Description",
        "content": "<div>Test Content</div>",
    }

    (tmp_path / "r123").mkdir(parents=True, exist_ok=True)

    # POST 요청으로 데이터 생성
    create_response = client.post("/api/v1/versions/r123/layouts", json=test_layout)
    assert create_response.status_code == status.HTTP_200_OK
    assert create_response.json()["name"] == test_layout["name"]

    # GET 요청으로 데이터 확인
    get_response = client.get("/api/v1/versions/r123/layouts")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 1
    assert get_response.json()[0]["name"] == test_layout["name"]


@pytest.mark.asyncio
async def test_invalid_layout_data(client: TestClient):
    """잘못된 레이아웃 데이터로 요청 시 테스트"""
    invalid_layout = {
        "name": "",  # 빈 이름
        "description": "Test Description",
        "content": "<div>Test Content</div>",
    }

    response = client.post("/api/v1/versions/r123/layouts", json=invalid_layout)
    assert response.status_code == 400
    assert "detail" in response.json()
