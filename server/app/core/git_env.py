"""Git 환경"""

import logging
import os
import subprocess
from typing import List

from app.models.common_model import User, VersionInfo

logger = logging.getLogger(__name__)


class GitEnv:
    """Git 환경"""

    def __init__(self, version_info: VersionInfo):
        self.version_info: VersionInfo = version_info

    def _run_command(self, command: str) -> None:
        """명령어 실행"""
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to execute command: {e.stderr.decode()}") from e

    def create_version(self):
        """Git 저장소 복제"""
        if self.version_info.is_root:
            raise ValueError("Root version cannot be cloned")

        efs_root_path = os.path.abspath(self.version_info.config.noti_temply_dir)
        try:
            # Clone the repository and create new branch
            command = (
                "git clone"
                " "
                f"--branch {self.version_info.config.noti_temply_main_version_name}"
                " "
                f"--single-branch {self.version_info.config.noti_temply_repo_url}"
                " "
                f"{efs_root_path}/{self.version_info.version}"
                " "
                f"&& cd {efs_root_path}/{self.version_info.version}"
                " "
                f"&& git checkout -b {self.version_info.version}"
                " "
                f"&& git push origin {self.version_info.version}"
            )
            self._run_command(command)
        except Exception as e:
            raise ValueError(f"Failed to clone repository: {e}") from e

    def delete_version(self):
        """Git 저장소 삭제"""
        if self.version_info.is_root:
            raise ValueError("Root version cannot be deleted")

        efs_root_path = os.path.abspath(self.version_info.config.noti_temply_dir)
        try:
            # 로컬 브랜치 삭제
            self._run_command(
                f"git -C {efs_root_path}/{self.version_info.version}"
                " "
                f"branch -D {self.version_info.version}"
            )
            # 원격 브랜치 삭제
            self._run_command(
                f"git -C {efs_root_path}/{self.version_info.version}"
                " "
                f"push origin --delete {self.version_info.version}"
            )
            # 디렉토리 삭제
            self._run_command(f"rm -rf {efs_root_path}/{self.version_info.version}")
        except Exception as e:
            raise ValueError(f"Failed to delete repository: {e}") from e

    def get_versions(self) -> List[VersionInfo]:
        """Git 저장소 목록 조회"""
        efs_root_path = os.path.abspath(self.version_info.config.noti_temply_dir)
        try:
            result = subprocess.run(
                f"git -C {efs_root_path}/{self.version_info.config.noti_temply_main_version_name}"
                " "
                f"fetch origin"
                " "
                f"&& git -C {efs_root_path}/{self.version_info.config.noti_temply_main_version_name}"
                " "
                f"branch -r",
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )
            git_branch_list = result.stdout.strip().split("\n")
            logger.debug("git_branch_list: %s", git_branch_list)
            return [
                VersionInfo(self.version_info.config, branch.strip().replace("origin/", ""))
                for branch in git_branch_list
                if branch.strip()  # 빈 문자열 제외
            ]
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to get versions: {e.stderr}") from e

    def commit_version(self, user: User, message: str, paths: List[str]):
        """Git 저장소 커밋"""
        if self.version_info.is_root:
            raise ValueError("Root version cannot be committed")

        efs_root_path = os.path.abspath(self.version_info.config.noti_temply_dir)
        try:
            # 삭제된 파일 처리
            deleted_files = [
                path
                for path in paths
                if not os.path.exists(os.path.join(efs_root_path, self.version_info.version, path))
            ]
            # 수정/추가된 파일 처리
            modified_files = [
                path
                for path in paths
                if os.path.exists(os.path.join(efs_root_path, self.version_info.version, path))
            ]

            commands = []
            if deleted_files:
                commands.append(
                    f"git -C {efs_root_path}/{self.version_info.version}"
                    f" rm {' '.join(deleted_files)}"
                )
            if modified_files:
                commands.append(
                    f"git -C {efs_root_path}/{self.version_info.version}"
                    f" add {' '.join(modified_files)}"
                )

            if commands:
                command = (
                    " && ".join(commands)
                    + f" && git -C {efs_root_path}/{self.version_info.version}"
                    + f" commit -m '{message}'"
                    + f" --author='{user.name} <{user.name}@noti-temply.com>'"
                    + f" && git -C {efs_root_path}/{self.version_info.version}"
                    + f" push origin {self.version_info.version}"
                )
                self._run_command(command)
        except Exception as e:
            raise ValueError(f"Failed to commit repository: {e}") from e
