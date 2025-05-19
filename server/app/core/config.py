"""
서버 설정
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    """서버 설정"""

    def __init__(self) -> None:
        # .env 파일 로드
        env_path = Path(__file__).parents[2] / ".env"
        load_dotenv(env_path)

        # 서버 설정
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "true").lower() == "true"

        # CORS 설정
        self.cors_origins = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))

        # 파일 설정
        self.file_encoding = "utf-8"

        self.noti_temply_dir: str = os.getenv("NOTI_TEMPLY_DIR", "noti-temply")


CONFIG = Config()
