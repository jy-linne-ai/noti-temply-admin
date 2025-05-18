from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from app.api import layouts, partials, templates
from app.core.config import Config


def create_app(config: Config):
    app = FastAPI(
        title="Noti Temply Admin",
        description="템플릿 관리 시스템",
        version="1.0.0",
    )

    app.state.config = config

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 등록
    # app.include_router(templates.router)
    # app.include_router(layout_api.router)
    # app.include_router(partials.router)

    return app


if __name__ == "__main__":
    app = create_app(Config())
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
