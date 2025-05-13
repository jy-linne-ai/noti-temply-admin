# Noti Temply Admin

템플릿 관리 시스템의 관리자 도구입니다.

## 프로젝트 구조

```
noti-temply-admin/
├── server/                # FastAPI 서버
│   ├── app/              # 애플리케이션 코드
│   ├── main.py           # 애플리케이션 진입점
│   ├── requirements.txt  # Python 의존성
│   └── .env             # 서버 환경변수
├── front/                # Next.js 프론트엔드
│   ├── src/             # 소스 코드
│   ├── package.json     # Node.js 의존성
│   ├── tsconfig.json    # TypeScript 설정
│   └── .env            # 프론트엔드 환경변수
├── templates/           # Jinja 템플릿 저장소
├── .gitignore          # Git 무시 파일
├── README.md           # 프로젝트 문서
└── docker-compose.yml  # Docker Compose 설정
```

## 시작하기

### 서버 실행

```bash
# FastAPI 서버
cd server
pip install -r requirements.txt
python main.py

# Next.js 서버
cd front
npm install
npm run dev
```

### 환경 변수 설정

#### 서버 (.env)
```
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
FRONTEND_URL=http://localhost:3000
```

#### 프론트엔드 (.env)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API 문서

서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 개발 가이드

### 서버 개발

1. Python 3.8 이상 필요
2. 가상환경 생성 및 활성화
3. 의존성 설치
4. 서버 실행

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 프론트엔드 개발

1. Node.js 18 이상 필요
2. 의존성 설치
3. 개발 서버 실행

```bash
npm install
npm run dev
```

## 라이선스

MIT 