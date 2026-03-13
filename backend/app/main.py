from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import admin, auth, orders, scores, search, tasks, upload
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Automated music transcription service platform API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(scores.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
