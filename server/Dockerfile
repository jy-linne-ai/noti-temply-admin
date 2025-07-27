# Python 3.11 베이스 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 Poetry 설치
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Poetry를 시스템에 설치
RUN pip install poetry

# Poetry 환경 변수 설정
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

ARG GIT_USER_NAME=noti-temply-admin
ARG GIT_USER_EMAIL=admin@noti-temply.com

# # Git 기본 설정 (root 사용자로)
# RUN git config --global user.name "${GIT_USER_NAME}" && \
#     git config --global user.email "${GIT_USER_EMAIL}"

# Poetry 설정 파일 복사
COPY pyproject.toml poetry.lock* ./

# 의존성 설치
RUN poetry install --only=main --no-root

# 애플리케이션 코드 복사
COPY . .

# 사용자 생성 (홈 디렉토리 포함)
RUN groupadd --system --gid 1001 python && \
    useradd --system --uid 1001 --gid python python --create-home

# 사용자 변경
USER python

RUN mkdir -p ~/.ssh
# GitHub SSH 호스트 키 등록 (python 사용자용)
RUN ssh-keyscan -H github.com >> ~/.ssh/known_hosts && \
    chown python:python ~/.ssh/known_hosts

# python 사용자용 Git 설정
RUN git config --global user.name "${GIT_USER_NAME}" && \
    git config --global user.email "${GIT_USER_EMAIL}"

ARG NOTI_TEMPLY_DIR=../../noti-temply-efs
ARG NOTI_TEMPLY_REPO_URL=git@github.com:mieeru/noti-temply.git

# 환경 변수 설정
ENV NOTI_TEMPLY_DIR=${NOTI_TEMPLY_DIR}
ENV NOTI_TEMPLY_REPO_URL=${NOTI_TEMPLY_REPO_URL}

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["poetry", "run", "python", "main.py"] 