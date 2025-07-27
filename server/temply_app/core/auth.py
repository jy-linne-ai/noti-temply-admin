"""GitHub OAuth 인증 모듈"""

import os
from typing import Dict, List, Optional

import httpx
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# GitHub OAuth 설정
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/api/auth/callback")

# 허용된 조직과 팀 설정
ALLOWED_ORGANIZATIONS = os.getenv("ALLOWED_ORGANIZATIONS", "").split(",")
ALLOWED_TEAMS = os.getenv("ALLOWED_TEAMS", "").split(",")

security = HTTPBearer()


class GitHubUser(BaseModel):
    id: int
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    organizations: List[str] = []
    teams: List[str] = []


class AuthService:
    """GitHub OAuth 인증 서비스"""

    @staticmethod
    async def get_access_token(code: str) -> str:
        """GitHub OAuth 코드로 액세스 토큰 획득"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": GITHUB_REDIRECT_URI,
                },
                headers={"Accept": "application/json"},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="GitHub OAuth 토큰 획득 실패"
                )

            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub OAuth 오류: {data.get('error_description', 'Unknown error')}",
                )

            return data["access_token"]

    @staticmethod
    async def get_user_info(access_token: str) -> GitHubUser:
        """액세스 토큰으로 사용자 정보 획득"""
        async with httpx.AsyncClient() as client:
            # 사용자 기본 정보
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="GitHub 사용자 정보 획득 실패"
                )

            user_data = user_response.json()

            # 사용자가 속한 조직 목록
            orgs_response = await client.get(
                "https://api.github.com/user/orgs",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            organizations = []
            if orgs_response.status_code == 200:
                orgs_data = orgs_response.json()
                organizations = [org["login"] for org in orgs_data]

            # 사용자가 속한 팀 목록
            teams_response = await client.get(
                "https://api.github.com/user/teams",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            teams = []
            if teams_response.status_code == 200:
                teams_data = teams_response.json()
                teams = [team["slug"] for team in teams_data]

            return GitHubUser(
                id=user_data["id"],
                login=user_data["login"],
                name=user_data.get("name"),
                email=user_data.get("email"),
                avatar_url=user_data.get("avatar_url"),
                organizations=organizations,
                teams=teams,
            )

    @staticmethod
    def check_authorization(user: GitHubUser) -> bool:
        """사용자의 조직/팀 멤버십 확인"""
        # 허용된 조직에 속해 있는지 확인
        has_allowed_org = any(org in ALLOWED_ORGANIZATIONS for org in user.organizations)

        if not has_allowed_org:
            return False

        # 허용된 팀에 속해 있는지 확인
        has_allowed_team = any(team in ALLOWED_TEAMS for team in user.teams)

        return has_allowed_team

    @staticmethod
    async def authenticate_user(code: str) -> GitHubUser:
        """OAuth 코드로 사용자 인증 및 권한 확인"""
        # 액세스 토큰 획득
        access_token = await AuthService.get_access_token(code)

        # 사용자 정보 획득
        user = await AuthService.get_user_info(access_token)

        # 권한 확인
        if not AuthService.check_authorization(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="접근 권한이 없습니다. 허용된 조직의 팀 멤버여야 합니다.",
            )

        return user


# JWT 토큰 관리 (선택사항)
class JWTService:
    """JWT 토큰 관리 서비스"""

    @staticmethod
    def create_token(user: GitHubUser) -> str:
        """사용자 정보로 JWT 토큰 생성"""
        # JWT 토큰 생성 로직 구현
        # 실제 구현에서는 python-jose 또는 PyJWT 사용
        return "dummy_token"  # 임시 구현

    @staticmethod
    def verify_token(token: str) -> Optional[GitHubUser]:
        """JWT 토큰 검증"""
        # JWT 토큰 검증 로직 구현
        return None  # 임시 구현
