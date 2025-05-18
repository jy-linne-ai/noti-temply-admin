"""App"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import layout_api, partial_api, template_api, template_item_api
from app.core.config import CONFIG


def create_app() -> FastAPI:
    """Create App"""
    app = FastAPI(
        title="Noti Temply Admin",
        description="템플릿 관리 시스템",
        version="1.0.0",
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CONFIG.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 등록
    app.include_router(template_api.router)
    app.include_router(layout_api.router)
    app.include_router(partial_api.router)
    app.include_router(template_item_api.router)

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
