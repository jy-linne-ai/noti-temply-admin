"""테스트 설정"""

import os
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from temply_app.apps import create_app
from temply_app.core.config import Config
from temply_app.core.temply.temply_env import TemplyEnv
from temply_app.models.common_model import User, VersionInfo


@pytest.fixture()
def data_env():
    """data 환경 설정"""
    base = Path(__file__).parent / "data"
    os.environ["env"] = "local"
    os.environ["NOTI_TEMPLY_DIR"] = str(base)
    conf = Config()
    return TemplyEnv(conf)


@pytest.fixture()
def temp_env(tmp_path):
    """테스트 환경 설정"""
    os.environ["env"] = "local"
    os.environ["NOTI_TEMPLY_DIR"] = str(tmp_path)
    conf = Config()
    return TemplyEnv(conf)


@pytest.fixture()
def user():
    """사용자 설정"""
    return User(name="test")


@pytest.fixture()
def version_info():
    """버전 정보 설정"""
    os.environ["env"] = "local"
    config = Config()
    return VersionInfo(config, "r123")


@pytest.fixture
def client(tmp_path) -> Generator[TestClient, None, None]:
    """테스트 클라이언트 설정"""

    os.environ["env"] = "local"
    os.environ["NOTI_TEMPLY_DIR"] = str(tmp_path)

    with TestClient(create_app(Config())) as test_client:
        yield test_client
