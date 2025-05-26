"""테스트 설정"""

import os
from pathlib import Path

import pytest

from app.core.config import Config
from app.core.temply.temply_env import TemplyEnv
from app.models.common_model import User, VersionInfo


@pytest.fixture()
def data_env():
    """data 환경 설정"""
    base = Path(__file__).parent / "data"
    os.environ["NOTI_TEMPLY_DIR"] = str(base)
    conf = Config()
    return TemplyEnv(conf)


@pytest.fixture()
def temp_env(tmp_path):
    """테스트 환경 설정"""
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
    config = Config()
    return VersionInfo(config, "r123")
