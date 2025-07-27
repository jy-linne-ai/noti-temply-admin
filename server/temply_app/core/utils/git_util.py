"""Git 유틸리티"""

import logging
import os
import subprocess
from shutil import rmtree
from typing import List

from temply_app.core.git_env import GitEnv
from temply_app.core.utils.cache_util import temply_version_env_cache_clear
from temply_app.models.common_model import User, VersionInfo

logger = logging.getLogger(__name__)


def _run_command(command: str) -> None:
    """명령어 실행"""
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to execute command: {e.stderr.decode()}") from e


class GitUtil:
    """Git 환경"""

    @staticmethod
    def _get_local_branch_list(git_env: GitEnv) -> List[str]:
        """로컬 파일에서 브랜치 목록 조회"""
        result = []
        for dir_name in os.listdir(git_env.efs_root_path):
            branch_path = os.path.join(git_env.efs_root_path, dir_name)
            if not os.path.isdir(branch_path) or dir_name.startswith("."):
                continue
            result.append(dir_name)
        return result

    @staticmethod
    def create_version(git_env: GitEnv) -> None:
        """Git 저장소 복제"""
        if git_env.version_info.is_root:
            raise ValueError("Root version cannot be cloned")

        try:
            command = (
                f"git clone --branch {git_env.config.noti_temply_main_version_name} "
                f"--single-branch {git_env.config.noti_temply_repo_url} {git_env.version_path} && "
                f"cd {git_env.version_path} && "
                f"git checkout -b {git_env.version_info.version} && "
                f"git push origin {git_env.version_info.version}"
            )
            _run_command(command)
        except Exception as e:
            raise ValueError(f"Failed to clone repository: {e}") from e

    @staticmethod
    def _refresh_main_version(git_env: GitEnv) -> None:
        """메인 버전 새로고침"""
        try:
            # 원격 저장소에서 최신 정보 가져오기 (삭제된 브랜치 정보도 정리)
            fetch_result = subprocess.run(
                f"git -C {git_env.efs_root_path}/{git_env.config.noti_temply_main_version_name} fetch --prune origin",
                shell=True,
                check=False,
                capture_output=True,
                text=True,
            )
            if fetch_result.returncode != 0:
                raise ValueError(f"Failed to fetch origin: {fetch_result.stderr}")
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to refresh main version: {e.stderr}") from e

    @staticmethod
    def delete_version(git_env: GitEnv) -> None:
        """버전 삭제"""
        if git_env.version_info.is_root:
            raise ValueError("Root version cannot be deleted")

        try:
            command = (
                f"cd {git_env.version_path} && "
                f"git checkout {git_env.config.noti_temply_main_version_name} && "
                f"git branch -D {git_env.version_info.version} && "
                f"git push origin --delete {git_env.version_info.version} && "
                f"rm -rf {git_env.version_path}"
            )
            _run_command(command)
            GitUtil.refresh_version(git_env)
        except Exception as e:
            raise ValueError(f"Failed to delete repository: {e}") from e

    @staticmethod
    def get_versions(git_env: GitEnv) -> List[VersionInfo]:
        """Git 저장소 목록 조회"""
        try:
            GitUtil._refresh_main_version(git_env)

            # 브랜치 목록 조회
            result = subprocess.run(
                f"git -C {git_env.efs_root_path}/{git_env.config.noti_temply_main_version_name} branch -r",
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )

            git_branch_list = [
                branch.strip().replace("origin/", "").split(" -> ")[-1]
                for branch in result.stdout.strip().split("\n")
                if branch.strip() and not branch.strip().startswith("origin/HEAD")
            ]

            # local에만 있는 브렌치가 있다면, 삭제해야 함.
            local_branch_list = GitUtil._get_local_branch_list(git_env)

            for local_branch in local_branch_list:
                if local_branch == git_env.config.noti_temply_main_version_name:
                    continue
                if local_branch not in git_branch_list:
                    rmtree(os.path.join(git_env.efs_root_path, local_branch))

            return [VersionInfo(git_env.config, branch) for branch in git_branch_list]

        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to get versions: {e.stderr}") from e

    @staticmethod
    def refresh_version(git_env: GitEnv) -> None:
        """버전 새로고침"""
        try:
            fetch_result = subprocess.run(
                f"git -C {git_env.efs_root_path}/{git_env.version_info.version} pull",
                shell=True,
                check=False,
                capture_output=True,
                text=True,
            )
            if fetch_result.returncode != 0:
                raise ValueError(f"Failed to fetch origin: {fetch_result.stderr}")
            if "Already up to date." in fetch_result.stdout.strip():
                logger.info("Already up to date for version %s", git_env.version_info.version)
            else:
                temply_version_env_cache_clear(git_env.version_info)
                logger.info(
                    "Successfully fetched origin for version %s", git_env.version_info.version
                )
        except subprocess.CalledProcessError as e:
            raise ValueError(
                f"Failed to refresh version {git_env.version_info.version}: {e.stderr}"
            ) from e

    @staticmethod
    def commit_version(git_env: GitEnv, user: User, message: str, paths: List[str]) -> None:
        """Git 저장소 커밋"""
        if git_env.version_info.is_root:
            raise ValueError("Root version cannot be committed")

        try:
            # 삭제된 파일 처리
            deleted_files = [
                path
                for path in paths
                if not os.path.exists(os.path.join(git_env.version_path, path))
            ]
            # 수정/추가된 파일 처리
            modified_files = [
                path for path in paths if os.path.exists(os.path.join(git_env.version_path, path))
            ]

            commands = []
            if deleted_files:
                commands.append(f"git -C {git_env.version_path} rm {' '.join(deleted_files)}")
            if modified_files:
                commands.append(f"git -C {git_env.version_path} add {' '.join(modified_files)}")

            if commands:
                command = (
                    " && ".join(commands)
                    + f" && git -C {git_env.version_path} commit -m '{message}'"
                    + f" --author='{user.name} <{user.name}@noti-temply.com>'"
                    + f" && git -C {git_env.version_path} pull origin {git_env.version_info.version}"
                    + f" && git -C {git_env.version_path} push origin {git_env.version_info.version}"
                )
                _run_command(command)
        except Exception as e:
            raise ValueError(f"Failed to commit repository: {e}") from e
