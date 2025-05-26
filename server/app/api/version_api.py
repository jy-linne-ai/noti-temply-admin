"""
Version API
"""

import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Config
from app.core.dependency import get_config
from app.core.git_env import GitEnv
from app.models.common_model import VersionInfo

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_versions(version_info: VersionInfo, git_env: Optional[GitEnv] = None) -> List[VersionInfo]:
    found_main_version = False

    if git_env:
        return git_env.get_versions()

    versions = []
    for dir_name in os.listdir(version_info.config.noti_temply_dir):
        if os.path.isdir(os.path.join(version_info.config.noti_temply_dir, dir_name)):
            versions.append(VersionInfo(version_info.config, dir_name))
            if dir_name == version_info.config.noti_temply_main_version_name:
                found_main_version = True

    if not found_main_version:
        raise HTTPException(status_code=400, detail="Main version not found")

    return versions


@router.get("", response_model=List[VersionInfo])
async def get_versions(config: Config = Depends(get_config)) -> List[VersionInfo]:
    """
    Get all versions
    """
    logger.info("Fetching all versions")
    git_env: GitEnv = GitEnv(VersionInfo.root_version(config))
    versions = _get_versions(VersionInfo.root_version(config), git_env)
    logger.info("Found %d versions", len(versions))
    return versions


@router.get("/{version}", response_model=VersionInfo)
async def get_version_info(version: str, config: Config = Depends(get_config)) -> VersionInfo:
    """
    Get version info
    """
    logger.info("Fetching info for version: %s", version)
    try:
        git_env: GitEnv = GitEnv(VersionInfo.root_version(config))
        version_info = next(
            v
            for v in _get_versions(VersionInfo.root_version(config), git_env)
            if v.version == version
        )
        logger.info("Found version info: %s", version_info)
        return version_info
    except StopIteration as exc:
        logger.error("Version not found: %s", version)
        raise HTTPException(status_code=404, detail=f"Version {version} not found") from exc


@router.post("", response_model=VersionInfo)
async def create_version(
    version: VersionInfo,
    config: Config = Depends(get_config),
) -> VersionInfo:
    """
    Create a new version
    """
    git_env: GitEnv = GitEnv(version)
    if version.is_root:
        raise HTTPException(status_code=400, detail="Cannot create main version")

    logger.info("Creating new version: %s", version.version)
    if git_env:
        return git_env.create_version()

    root_full_path = os.path.abspath(config.noti_temply_dir)
    try:
        # Clone the repository and create new branch
        os.system(
            f"git clone --branch {config.noti_temply_main_version_name} "
            f"--single-branch git@github.com:jy-linne-ai/noti-temply.git {root_full_path}/{version.version} && "
            f"cd {root_full_path}/{version.version} && "
            f"git checkout -b {version.version} && "
            f"git push origin {version.version}"
        )
        logger.info("Successfully created version: %s", version.version)
        return version
    except Exception as e:
        logger.error("Failed to create version %s: %s", version.version, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create version: {str(e)}") from e


@router.delete("/{version}")
async def delete_version(version: str, config: Config = Depends(get_config)) -> None:
    """
    Delete a version
    """
    logger.info("Attempting to delete version: %s", version)
    git_env: GitEnv = GitEnv(VersionInfo(config, version))
    if git_env:
        return git_env.delete_version()

    if version == config.noti_temply_main_version_name:
        logger.warning("Attempted to delete main version: %s", version)
        raise HTTPException(status_code=400, detail="Cannot delete main version")
    try:
        # 로컬 브랜치 삭제
        os.system(f"git -C {config.noti_temply_dir}/{version} branch -D {version}")
        # 원격 브랜치 삭제
        os.system(f"git -C {config.noti_temply_dir}/{version} push origin --delete {version}")
        # 디렉토리 삭제
        os.system(f"rm -rf {config.noti_temply_dir}/{version}")
        logger.info("Successfully deleted version: %s", version)
    except Exception as e:
        logger.error("Failed to delete version %s: %s", version, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete version: {str(e)}") from e
