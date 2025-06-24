"""
Version API
"""

import logging
import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from temply_app.core.config import Config
from temply_app.core.dependency import get_config, get_version_info
from temply_app.core.git_env import GitEnv
from temply_app.models.common_model import CreateVersionRequest, ReturnVersionInfo, VersionInfo

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_versions(git_env: GitEnv) -> List[ReturnVersionInfo]:
    versions = []
    for v in git_env.get_versions():
        _git_env = GitEnv(git_env.config, v)
        if not v.is_root and not os.path.exists(_git_env.version_path):
            _git_env.create_version()

        versions.append(ReturnVersionInfo(version=v.version, is_root=v.is_root))
    if not versions:
        raise HTTPException(status_code=404, detail="No versions found")
    return versions


@router.get("", response_model=List[ReturnVersionInfo])
async def get_versions(config: Config = Depends(get_config)) -> List[ReturnVersionInfo]:
    """
    Get all versions
    """
    logger.info("Fetching all versions")
    git_env: GitEnv = GitEnv(config, VersionInfo.root_version(config))
    versions = _get_versions(git_env)
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
            v for v in _get_versions(git_env) if v.version == version_info.version
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
    git_env.create_version()
    return ReturnVersionInfo(version=version_info.version, is_root=version_info.is_root)


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
    git_env.delete_version()
