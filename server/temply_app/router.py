"""Router"""

from fastapi import APIRouter, FastAPI

from temply_app.api import (
    layout_api,
    partial_api,
    system_api,
    template_api,
    template_name_api,
    version_api,
)


def set_router(app: FastAPI) -> None:
    """Get Router"""

    router = APIRouter()
    router.include_router(layout_api.router, prefix="/versions/{version}/layouts", tags=["layouts"])
    router.include_router(
        partial_api.router, prefix="/versions/{version}/partials", tags=["partials"]
    )
    router.include_router(
        template_api.router, prefix="/versions/{version}/templates", tags=["templates"]
    )

    router.include_router(version_api.router, prefix="/versions", tags=["versions"])
    router.include_router(
        template_name_api.router,
        prefix="/versions/{version}/template-names",
        tags=["template-names"],
    )
    router.include_router(system_api.router, prefix="/system", tags=["system"])

    app.include_router(router, prefix="/api/v1")
