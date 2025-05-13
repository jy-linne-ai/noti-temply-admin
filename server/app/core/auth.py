from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """현재 사용자의 ID를 반환합니다."""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: JWT 토큰 검증 로직 추가
    # 현재는 임시로 토큰 값을 사용자 ID로 사용
    return credentials.credentials 