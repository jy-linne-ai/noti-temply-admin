from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import layouts, partials, templates
from app.core.config import CORS_ORIGINS, HOST, PORT

app = FastAPI(
    title="Noti Temply Admin",
    description="템플릿 관리 시스템",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(templates.router)
app.include_router(layouts.router)
app.include_router(partials.router)


@app.get("/")
async def root():
    return {"message": "Noti Temply Admin API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
