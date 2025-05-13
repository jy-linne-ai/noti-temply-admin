# Noti Temply Admin Server

템플릿 관리 서버입니다. 템플릿, 레이아웃, 파트를 파일 시스템으로 관리합니다.

## 개발 환경 설정

### 1. Conda 환경 설정

```bash
# Conda 환경 생성
conda env create -f environment.yml

# Conda 환경 활성화
conda activate noti-temply-admin
```

### 2. Poetry 의존성 설치

```bash
# 서버 디렉토리로 이동
cd server

# Poetry 의존성 설치
poetry install
```

## 개발 도구

### 코드 포맷팅

```bash
# Black으로 코드 포맷팅
poetry run black .

# isort로 import 정렬
poetry run isort .
```

### 린트 및 타입 체크

```bash
# Flake8으로 린트
poetry run flake8

# MyPy로 타입 체크
poetry run mypy .
```

## 서버 실행

### 개발 모드

```bash
# 서버 실행
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 프로덕션 모드

```bash
# 서버 실행
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

## API 문서

서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
server/
├── app/
│   ├── api/          # API 엔드포인트
│   ├── core/         # 핵심 설정
│   └── services/     # 비즈니스 로직
├── environment.yml   # Conda 환경 설정
├── pyproject.toml    # Poetry 의존성 및 도구 설정
└── main.py          # 애플리케이션 진입점
```

## 파일 시스템 구조

템플릿, 레이아웃, 파트는 각각 별도의 디렉토리에서 관리됩니다:

```
templates/
├── {template_id}.json    # 템플릿 메타데이터
└── {template_id}.jinja   # 템플릿 내용

layouts/
├── {layout_id}.json      # 레이아웃 메타데이터
└── {layout_id}.jinja     # 레이아웃 내용

parts/
├── {part_id}.json        # 파트 메타데이터
└── {part_id}.jinja       # 파트 내용
```

각 JSON 파일에는 다음 정보가 포함됩니다:
- id: 고유 식별자
- name: 이름
- description: 설명
- variables: 변수 목록
- created_at: 생성일
- updated_at: 수정일

## 환경 변수

`.env` 파일을 생성하여 다음 환경 변수를 설정할 수 있습니다:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]

# 템플릿 디렉토리 설정
TEMPLATES_DIR="../templates"
LAYOUTS_DIR="../layouts"
PARTS_DIR="../parts"
```

## 라이선스

MIT 