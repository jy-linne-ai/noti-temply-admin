"""Apps"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from temply_app.core.config import Config
from temply_app.router import set_router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) 

def create_app(config: Config) -> FastAPI:
    """Create App"""
    app = FastAPI(
        title="Noti Temply Admin",
        description="템플릿 관리 시스템",
        version="1.0.0",
    )

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
        logger.error(f"ValueError: {str(exc)}")
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"},
        )

    # 라우터 설정
    set_router(app)

    return app


def get_app() -> FastAPI:
    """Get App"""
    return create_app(Config())
