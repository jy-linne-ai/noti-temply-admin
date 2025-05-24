"""App"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from app.api import layout_api, partial_api, template_api, template_item_api, version_api
from app.core.config import CONFIG


def create_app() -> FastAPI:
    """Create App"""
    app = FastAPI(title="Noti Temply Admin", description="템플릿 관리 시스템", version="1.0.0")

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CONFIG.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    router = APIRouter()
    router.include_router(layout_api.router, prefix="/versions/{version}/layouts", tags=["layouts"])
    router.include_router(
        partial_api.router, prefix="/versions/{version}/partials", tags=["partials"]
    )
    router.include_router(
        template_api.router, prefix="/versions/{version}/templates", tags=["templates"]
    )

    router.include_router(
        template_item_api.router, prefix="/template-items", tags=["template-items"]
    )
    router.include_router(version_api.router, prefix="/versions", tags=["versions"])

    app.include_router(router, prefix="/api/v1")
    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
