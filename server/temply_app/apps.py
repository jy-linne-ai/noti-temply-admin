from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from temply_app.api import (
    layout_api,
    partial_api,
    template_api,
    template_default_component_name_api,
    template_name_api,
    version_api,
)
from temply_app.core.config import Config


def create_app(config: Config) -> FastAPI:
    """Create App"""
    app = FastAPI(title="Noti Temply Admin", description="템플릿 관리 시스템", version="1.0.0")

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 전역 예외 핸들러
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"},
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
        template_default_component_name_api.router,
        prefix="/template-available-components",
        tags=["template-available-components"],
    )
    router.include_router(version_api.router, prefix="/versions", tags=["versions"])
    router.include_router(
        template_name_api.router,
        prefix="/versions/{version}/template-names",
        tags=["template-names"],
    )

    app.include_router(router, prefix="/api/v1")
    #
    return app


def get_app() -> FastAPI:
    """Get App"""
    return create_app(Config())
