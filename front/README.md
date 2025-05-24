# Noti Temply Admin Frontend

템플릿 관리 시스템의 프론트엔드 애플리케이션입니다.

## 기술 스택

- Next.js 14
- TypeScript
- Material-UI (MUI)
- NextAuth.js
- React

## 시작하기

### 필수 조건

- Node.js 18.0.0 이상
- npm 또는 yarn

### 환경 설정

1. 프로젝트 루트에 `.env.local` 파일을 생성하고 다음 환경 변수를 설정합니다:

```env
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. 의존성 설치:

```bash
npm install
# 또는
yarn install
```

3. 개발 서버 실행:

```bash
npm run dev
# 또는
yarn dev
```

4. 브라우저에서 `http://localhost:3000`으로 접속합니다.

## 주요 기능

- 템플릿 관리
  - 템플릿 생성, 조회, 수정, 삭제
  - 템플릿 미리보기
  - 변수 스키마 관리

- 레이아웃 관리
  - 레이아웃 생성, 조회, 수정, 삭제
  - 레이아웃 미리보기

- 파셜 관리
  - 파셜 생성, 조회, 수정, 삭제
  - 파셜 미리보기
  - 부모-자식 관계 관리

## 인증

- NextAuth.js를 사용한 인증 시스템
- JWT 기반 세션 관리
- 보호된 라우트에 대한 미들웨어 적용

### 기본 관리자 계정

- 아이디: admin
- 비밀번호: admin

## 프로젝트 구조

```
src/
├── app/                    # Next.js 13+ App Router
│   ├── (dashboard)/       # 대시보드 레이아웃
│   ├── auth/             # 인증 관련 페이지
│   └── api/              # API 라우트
├── components/            # 재사용 가능한 컴포넌트
├── lib/                   # 유틸리티 함수 및 설정
├── services/             # API 서비스
└── types/                # TypeScript 타입 정의
```

## 개발 가이드

### 컴포넌트 작성

- Material-UI 컴포넌트를 기본으로 사용
- 재사용 가능한 컴포넌트는 `components` 디렉토리에 작성
- 페이지별 컴포넌트는 해당 페이지 디렉토리에 작성

### API 호출

```typescript
import { getSession } from "next-auth/react";

const session = await getSession();
const response = await fetch(API_URL, {
  headers: {
    Authorization: `Bearer ${session?.accessToken}`,
  },
});
```

### 스타일링

- Material-UI의 `sx` prop을 사용한 인라인 스타일링
- 필요한 경우 `styled` API 사용
- 글로벌 스타일은 `app/layout.tsx`에서 관리

## 배포

1. 프로덕션 빌드:

```bash
npm run build
# 또는
yarn build
```

2. 프로덕션 서버 실행:

```bash
npm run start
# 또는
yarn start
```

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 