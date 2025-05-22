"""Temply 버전별 환경 관리"""

from app.core.config import Config
from app.core.temply.temply_env import TemplyEnv


class TemplyVersionEnv:
    """Temply 버전별 환경"""

    def __init__(self, config: Config, version: str, pr_version: str | None = None):
        self.version: str = version
        self.pr_version: str | None = pr_version
        self.applied_version: str

        # TODO 실제 버전 목록을 조회하는 로직 추가
        # 목록중 input 버전과 일치하는 버전을 찾아서 적용
        # 일치하는 버전이 없으면 Pr 버전이 있는지 확인
        # Pr 버전이 있으면 Pr 버전을 적용
        # 2개 모두 없으면 예외 발생
        if config.is_dev() and pr_version:
            self.applied_version = pr_version
        else:
            self.applied_version = version
        self.temply_env: TemplyEnv = TemplyEnv(config, self.applied_version)

    def get_temply_env(self) -> TemplyEnv:
        """Temply 환경 반환"""
        return self.temply_env

    def get_applied_version(self) -> str:
        """적용된 버전 반환"""
        return self.applied_version
