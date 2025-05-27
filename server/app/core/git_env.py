"""Git 환경"""

import logging
import os
import subprocess
from typing import List

from app.core.config import Config
from app.models.common_model import User, VersionInfo

logger = logging.getLogger(__name__)


class GitEnv:
    """Git 환경"""

    def __init__(self, config: Config, version_info: VersionInfo):
        self.config = config
        self.version_info: VersionInfo = version_info
        self.efs_root_path = os.path.abspath(self.config.noti_temply_dir)
        self.version_path = f"{self.efs_root_path}/{self.version_info.version}"

    def _run_command(self, command: str) -> None:
        """명령어 실행"""
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to execute command: {e.stderr.decode()}") from e

    def create_version(self) -> None:
        """Git 저장소 복제"""
        if self.version_info.is_root:
            raise ValueError("Root version cannot be cloned")

        try:
            command = (
                f"git clone --branch {self.config.noti_temply_main_version_name} "
                f"--single-branch {self.config.noti_temply_repo_url} {self.version_path} && "
                f"cd {self.version_path} && "
                f"git checkout -b {self.version_info.version} && "
                f"git push origin {self.version_info.version}"
            )
            self._run_command(command)
        except Exception as e:
            raise ValueError(f"Failed to clone repository: {e}") from e

    def _refresh_main_version(self) -> None:
        """메인 버전 새로고침"""
        try:
            # 원격 저장소에서 최신 정보 가져오기 (삭제된 브랜치 정보도 정리)
            fetch_result = subprocess.run(
                f"git -C {self.efs_root_path}/{self.config.noti_temply_main_version_name} fetch --prune origin",
                shell=True,
                check=False,
                capture_output=True,
                text=True,
            )
            if fetch_result.returncode != 0:
                logger.warning("Failed to fetch origin: %s", fetch_result.stderr)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to refresh main version: %s", e.stderr)

    def delete_version(self) -> None:
        """버전 삭제"""
        if self.version_info.is_root:
            raise ValueError("Root version cannot be deleted")

        try:
            command = (
                f"cd {self.version_path} && "
                f"git checkout {self.config.noti_temply_main_version_name} && "
                f"git branch -D {self.version_info.version} && "
                f"git push origin --delete {self.version_info.version} && "
                f"rm -rf {self.version_path}"
            )
            self._run_command(command)
            # self._refresh_main_version()
        except Exception as e:
            raise ValueError(f"Failed to delete repository: {e}") from e

    def get_versions(self) -> List[VersionInfo]:
        """Git 저장소 목록 조회"""
        try:
            self._refresh_main_version()

            # 브랜치 목록 조회
            result = subprocess.run(
                f"git -C {self.efs_root_path}/{self.config.noti_temply_main_version_name} branch -r",
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )
            git_branch_list = result.stdout.strip().split("\n")
            logger.debug("git_branch_list: %s", git_branch_list)
            return [
                VersionInfo(self.config, branch.strip().replace("origin/", "").split(" -> ")[-1])
                for branch in git_branch_list
                if branch.strip() and not branch.strip().startswith("origin/HEAD")  # 빈 문자열 제외
            ]
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to get versions: {e.stderr}") from e

    def commit_version(self, user: User, message: str, paths: List[str]) -> None:
        """Git 저장소 커밋"""
        if self.version_info.is_root:
            raise ValueError("Root version cannot be committed")

        try:
            # 삭제된 파일 처리
            deleted_files = [
                path for path in paths if not os.path.exists(os.path.join(self.version_path, path))
            ]
            # 수정/추가된 파일 처리
            modified_files = [
                path for path in paths if os.path.exists(os.path.join(self.version_path, path))
            ]

            commands = []
            if deleted_files:
                commands.append(f"git -C {self.version_path} rm {' '.join(deleted_files)}")
            if modified_files:
                commands.append(f"git -C {self.version_path} add {' '.join(modified_files)}")

            if commands:
                command = (
                    " && ".join(commands)
                    + f" && git -C {self.version_path} commit -m '{message}'"
                    + f" --author='{user.name} <{user.name}@noti-temply.com>'"
                    + f" && git -C {self.version_path} push origin {self.version_info.version}"
                )
                self._run_command(command)
        except Exception as e:
            raise ValueError(f"Failed to commit repository: {e}") from e
