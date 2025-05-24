from typing import List

from fastapi import APIRouter

from app.models.common_model import VersionInfo

router = APIRouter()

_versions = [
    VersionInfo(version="r1", is_root=False),
    VersionInfo(version="r1_pr123", is_root=False),
    VersionInfo(version="root", is_root=True),
]


@router.get("", response_model=List[VersionInfo])
async def get_versions() -> List[VersionInfo]:
    return _versions


@router.get("/{version}", response_model=VersionInfo)
async def get_version_info(version: str) -> VersionInfo:
    return next((v for v in _versions if v.version == version), None)


@router.post("", response_model=VersionInfo)
async def create_version(version: VersionInfo) -> VersionInfo:
    _versions.append(version)
    return version


@router.delete("/{version}")
async def delete_version(version: str) -> None:
    _versions.remove(next((v for v in _versions if v.version == version), None))
