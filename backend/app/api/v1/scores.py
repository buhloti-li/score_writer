import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_admin_user
from app.models.user import User
from app.schemas.score import ScoreCreate, ScoreListResponse, ScoreResponse, ScoreUpdate
from app.services.score_service import ScoreService, ScoreServiceError

router = APIRouter(prefix="/scores", tags=["scores"])


@router.get("", response_model=ScoreListResponse)
async def list_scores(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    instrument: str | None = None,
    composer: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    session: AsyncSession = Depends(get_db),
):
    service = ScoreService(session)
    offset = (page - 1) * page_size

    if instrument:
        items = await service.list_by_instrument(instrument, offset, page_size)
        total = len(items)
    elif composer:
        items = await service.list_by_composer(composer, offset, page_size)
        total = len(items)
    elif min_price is not None and max_price is not None:
        try:
            items = await service.list_by_price_range(min_price, max_price, offset, page_size)
        except ScoreServiceError as e:
            raise HTTPException(status_code=400, detail=str(e))
        total = len(items)
    else:
        items, total = await service.list_scores(offset, page_size)

    return ScoreListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{score_id}", response_model=ScoreResponse)
async def get_score(score_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    service = ScoreService(session)
    try:
        return await service.get_score(score_id)
    except ScoreServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
async def create_score(
    data: ScoreCreate,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = ScoreService(session)
    return await service.create_score(data)


@router.put("/{score_id}", response_model=ScoreResponse)
async def update_score(
    score_id: uuid.UUID,
    data: ScoreUpdate,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = ScoreService(session)
    try:
        return await service.update_score(score_id, data)
    except ScoreServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_score(
    score_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = ScoreService(session)
    try:
        await service.delete_score(score_id)
    except ScoreServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
