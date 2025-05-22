"""
서버 설정
"""

from typing import List

from pydantic_settings import BaseSettings


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
    noti_temply_dir: str = "noti-temply"

    def is_local(self) -> bool:
        """로컬 환경 여부"""
        return self.env == "local"

    def is_dev(self) -> bool:
        """개발 환경 여부"""
        return self.env in self.dev_envs.split(",")

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins 리스트"""
        return self.cors_origins.split(",")

    class Config:
        """설정"""

        env_file = ".env"
        env_parse_array_values = True  # 쉼표로 구분된 문자열을 리스트로 자동 변환


CONFIG = Config()
