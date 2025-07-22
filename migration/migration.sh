#!/bin/bash

# MySQL 데이터를 파일로 저장하는 마이그레이션 스크립트

echo "🚀 MySQL 데이터 마이그레이션을 시작합니다..."

export DATABASE_URL="mysql+pymysql://root:1234@localhost:3306/noti_temply"

# uv run으로 스크립트 실행
uv run python migration_db_to_files.py "$@" 
