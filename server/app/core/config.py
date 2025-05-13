"""
서버 설정
"""

import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 기본 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
NOTI_TEMPLY_DIR = BASE_DIR.parent / "noti-temply"

# 디렉토리 경로
TEMPLATES_DIR = NOTI_TEMPLY_DIR / "templates"
LAYOUTS_DIR = NOTI_TEMPLY_DIR / "layouts"
PARTIALS_DIR = NOTI_TEMPLY_DIR / "partials"

# 서버 설정
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# CORS 설정
CORS_ORIGINS: List[str] = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))

# 파일 설정
FILE_ENCODING = "utf-8"

# 메타데이터 파일명
SCHEMA_FILE = "schema.json"  # 변수 정의
CONTENT_FILE = "content.txt"  # 템플릿 내용
METADATA_FILE = "metadata.json"  # 메타데이터
