"""
Version API
"""

import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Config
from app.core.dependency import get_config, get_version_info
from app.core.git_env import GitEnv
from app.models.common_model import CreateVersionRequest, ReturnVersionInfo, VersionInfo

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_versions(config: Config, git_env: Optional[GitEnv] = None) -> List[ReturnVersionInfo]:
    found_main_version = False

    if git_env:
        return [
            ReturnVersionInfo(version=v.version, is_root=v.is_root) for v in git_env.get_versions()
        ]

    versions = []
    for dir_name in os.listdir(config.noti_temply_dir):
        if os.path.isdir(os.path.join(config.noti_temply_dir, dir_name)):
            versions.append(VersionInfo(config, dir_name))
            if dir_name == config.noti_temply_main_version_name:
                found_main_version = True

    if not found_main_version:
        raise HTTPException(status_code=400, detail="Main version not found")

    return [ReturnVersionInfo(version=v.version, is_root=v.is_root) for v in versions]


@router.get("", response_model=List[ReturnVersionInfo])
async def get_versions(config: Config = Depends(get_config)) -> List[ReturnVersionInfo]:
    """
    Get all versions
    """
    logger.info("Fetching all versions")
    git_env: GitEnv = GitEnv(config, VersionInfo.root_version(config))
    versions = _get_versions(config, git_env)
    logger.info("Found %d versions", len(versions))
    return versions


@router.get("/{version}", response_model=ReturnVersionInfo)
async def get_version_info_by_version(
    version_info: VersionInfo = Depends(get_version_info),
    config: Config = Depends(get_config),
) -> ReturnVersionInfo:
    """
    Get version info
    """
    logger.info("Fetching info for version: %s", version_info.version)
    try:
        git_env: GitEnv = GitEnv(config, version_info)
        return_version_info = next(
            v for v in _get_versions(config, git_env) if v.version == version_info.version
        )
        logger.info("Found version info: %s", return_version_info)
        return return_version_info
    except StopIteration as exc:
        logger.error("Version not found: %s", version_info.version)
        raise HTTPException(
            status_code=404, detail=f"Version {version_info.version} not found"
        ) from exc


@router.post("", response_model=ReturnVersionInfo)
async def create_version(
    request: CreateVersionRequest,
    config: Config = Depends(get_config),
) -> ReturnVersionInfo:
    """
    Create a new version
    """
    # make version info
    version_info = VersionInfo(config=config, version=request.version)
    git_env: GitEnv = GitEnv(config, version_info)
    if version_info.is_root:
        raise HTTPException(status_code=400, detail="Cannot create main version")

    logger.info("Creating new version: %s", request.version)
    if git_env:
        git_env.create_version()
        return ReturnVersionInfo(version=version_info.version, is_root=version_info.is_root)

    root_full_path = os.path.abspath(config.noti_temply_dir)
    try:
        # Clone the repository and create new branch
        os.system(
            f"git clone --branch {config.noti_temply_main_version_name} "
            f"--single-branch git@github.com:jy-linne-ai/noti-temply.git {root_full_path}/{request.version} && "
            f"cd {root_full_path}/{request.version} && "
            f"git checkout -b {request.version} && "
            f"git push origin {request.version}"
        )
        logger.info("Successfully created version: %s", request.version)
        return ReturnVersionInfo(version=request.version, is_root=version_info.is_root)
    except Exception as e:
        logger.error("Failed to create version %s: %s", request.version, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create version: {str(e)}") from e


@router.delete("/{version}")
async def delete_version(
    version_info: VersionInfo = Depends(get_version_info),
    config: Config = Depends(get_config),
) -> None:
    """
    Delete a version
    """
    logger.info("Attempting to delete version: %s", version_info.version)
    git_env: GitEnv = GitEnv(config, version_info)
    if git_env:
        return git_env.delete_version()

    if version_info.is_root:
        logger.warning("Attempted to delete main version: %s", version_info.version)
        raise HTTPException(status_code=400, detail="Cannot delete main version")
    try:
        # Git 명령어들을 하나로 연결
        os.system(
            f"cd {config.noti_temply_dir}/{version_info.version} && "
            f"git checkout {config.noti_temply_main_version_name} && "
            f"git branch -D {version_info.version} && "
            f"git push origin --delete {version_info.version} && "
            f"cd .. && "
            f"rm -rf {version_info.version}"
        )
        logger.info("Successfully deleted version: %s", version_info.version)
    except Exception as e:
        logger.error("Failed to delete version %s: %s", version_info.version, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete version: {str(e)}") from e
