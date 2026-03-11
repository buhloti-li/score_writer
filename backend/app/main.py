from fastapi import FastAPI

from app.api.v1 import auth, orders, scores, tasks
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Automated music transcription service platform API",
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(scores.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
