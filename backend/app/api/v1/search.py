from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.score import ScoreListResponse
from app.services.score_service import ScoreService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=ScoreListResponse)
async def search_scores(
    q: str = Query("", min_length=0),
    instrument: str | None = None,
    genre: str | None = None,
    difficulty: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    service = ScoreService(session)
    offset = (page - 1) * page_size
    items, total = await service.search_scores(
        query=q,
        instrument=instrument,
        genre=genre,
        difficulty=difficulty,
        offset=offset,
        limit=page_size,
    )
    return ScoreListResponse(items=items, total=total, page=page, page_size=page_size)
