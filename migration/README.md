# Database Migration Tool

MySQL 데이터를 JSON 파일로 내보내는 마이그레이션 도구입니다.

## 📋 목차

- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [사용법](#사용법)
- [옵션](#옵션)
- [출력](#출력)
- [개발](#개발)

## 🚀 설치

```bash
# uv 설치 (아직 설치되지 않은 경우)
pip install uv

# 의존성 설치
uv sync
```

## ⚡ 빠른 시작

```bash
# 기본 설정으로 실행
uv run python migration_db_to_files.py

# 또는 스크립트 사용
./migration.sh
```

## 📖 사용법

### 1. 기본 실행

```bash
# 기본 설정으로 실행
uv run python migration_db_to_files.py
```

### 2. 커스텀 설정으로 실행

```bash
uv run python migration_db_to_files.py \
  --host localhost \
  --user myuser \
  --password mypassword \
  --database mydb \
  --output ./my_export
```

### 3. 스크립트 사용 (권장)

```bash
# 실행 권한 부여 (최초 1회)
chmod +x migration.sh

# 스크립트 실행
./migration.sh

# 추가 옵션과 함께 실행
./migration.sh --output ./custom_export
```

### 4. 도움말 보기

```bash
uv run python migration_db_to_files.py --help
```

## ⚙️ 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--host` | MySQL 호스트 | `127.0.0.1` |
| `--user` | MySQL 사용자 | `root` |
| `--password` | MySQL 비밀번호 | `1234` |
| `--database` | 데이터베이스 이름 | `noti_temply` |
| `--output` | 출력 디렉토리 | `./exported_data` |

## 📁 출력

스크립트는 지정된 출력 디렉토리에 각 테이블별로 JSON 파일을 생성합니다:

```
exported_data/
├── users.json
├── templates.json
├── layouts.json
├── partials.json
└── ...
```

## 🛠️ 개발

### 의존성 관리

```bash
# 개발 의존성 설치
uv sync --dev

# 의존성 업데이트
uv sync --upgrade
```

### 코드 품질

```bash
# 코드 포맷팅
uv run black .

# 린팅
uv run flake8 .

# 타입 체크
uv run mypy .
```

### 테스트

```bash
# 테스트 실행
uv run pytest

# 테스트 커버리지
uv run pytest --cov=.
```

## 📝 예시

### 프로덕션 환경에서 실행

```bash
uv run python migration_db_to_files.py \
  --host 192.168.1.100 \
  --user admin \
  --password secure123 \
  --database production_db \
  --output ./backup_data
```

### 로컬 개발 환경에서 실행

```bash
# 기본 설정 사용
./migration.sh

# 커스텀 출력 디렉토리
./migration.sh --output ./local_export
```

## 🔧 문제 해결

### 일반적인 문제

1. **연결 오류**: 데이터베이스 호스트, 사용자, 비밀번호 확인
2. **권한 오류**: 스크립트 실행 권한 확인 (`chmod +x migration.sh`)
3. **의존성 오류**: `uv sync` 재실행

### 로그 확인

```bash
# 상세 로그와 함께 실행
uv run python migration_db_to_files.py --verbose
``` 