"""
서버 설정
"""

import logging
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """서버 설정"""

    # 서버 설정
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    env: str = "dev"
    dev_envs: str = "dev,bx"  # 쉼표로 구분된 문자열로 받음
    cors_origins: str = "http://localhost:3000"  # 쉼표로 구분된 문자열로 받음

    # 파일 설정
    file_encoding: str = "utf-8"
    noti_temply_repo_url: str = ""
    # "git@github.com:jy-linne-ai/noti-temply.git"
    noti_temply_dir: str = "noti-temply"
    noti_temply_main_version_name: str = "main"

    def is_local(self) -> bool:
        """로컬 환경 여부"""
        return self.env == "local"

    def is_dev(self) -> bool:
        """개발 환경 여부"""
        return self.env in self.dev_envs.split(",")

    def is_git_used(self) -> bool:
        """git 사용 여부"""
        return self.noti_temply_repo_url != ""

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins 리스트"""
        return self.cors_origins.split(",")

    model_config = SettingsConfigDict(
        env_file=".env",
    )

    def __post_init__(self):
        """설정 초기화 후 로깅"""
        logger.info("Config initialized: %s", self)
