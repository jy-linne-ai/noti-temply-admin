"""Temply 버전별 환경 관리"""

from temply_app.core.config import Config
from temply_app.core.git_env import GitEnv
from temply_app.core.temply.temply_env import TemplyEnv
from temply_app.models.common_model import VersionInfo


class TemplyVersionEnv:
    """Temply 버전별 환경"""

    def __init__(self, config: Config, version_info: VersionInfo, git_env: GitEnv | None = None):
        self.version_info: VersionInfo = version_info
        self.applied_version: str
        self.git_env: GitEnv | None = git_env

        # TODO 실제 버전 목록을 조회하는 로직 추가
        # 목록중 input 버전과 일치하는 버전을 찾아서 적용
        # 일치하는 버전이 없으면 Pr 버전이 있는지 확인
        # Pr 버전이 있으면 Pr 버전을 적용
        # 2개 모두 없으면 예외 발생
        # if config.is_dev() and self.version_info.pr_number:
        #     self.applied_version = self.version_info.pr_number
        # else:
        #     self.applied_version = self.version_info.revision_version
        self.temply_env: TemplyEnv = TemplyEnv(config, self.version_info.version, git_env=git_env)

    def get_temply_env(self) -> TemplyEnv:
        """Temply 환경 반환"""
        return self.temply_env

    def get_applied_version(self) -> str:
        """적용된 버전 반환"""
        return self.applied_version
