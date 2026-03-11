from decimal import Decimal
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.score import CopyrightType, Score, ScoreStatus
from app.repositories.base import BaseRepository


class ScoreRepository(BaseRepository[Score]):
    def __init__(self, session: AsyncSession):
        super().__init__(Score, session)

    async def get_available(
        self, offset: int = 0, limit: int = 20
    ) -> Sequence[Score]:
        stmt = (
            select(Score)
            .where(Score.status == ScoreStatus.AVAILABLE)
            .where(Score.copyright_status.in_([CopyrightType.PUBLIC_DOMAIN, CopyrightType.LICENSED]))
            .order_by(Score.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_instrument(
        self, instrument: str, offset: int = 0, limit: int = 20
    ) -> Sequence[Score]:
        stmt = (
            select(Score)
            .where(Score.instrument == instrument)
            .where(Score.status == ScoreStatus.AVAILABLE)
            .order_by(Score.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_composer(
        self, composer: str, offset: int = 0, limit: int = 20
    ) -> Sequence[Score]:
        stmt = (
            select(Score)
            .where(Score.composer == composer)
            .where(Score.status == ScoreStatus.AVAILABLE)
            .order_by(Score.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_price_range(
        self,
        min_price: Decimal,
        max_price: Decimal,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Score]:
        stmt = (
            select(Score)
            .where(Score.price >= min_price, Score.price <= max_price)
            .where(Score.status == ScoreStatus.AVAILABLE)
            .order_by(Score.price.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def increment_download_count(self, score_id) -> None:
        score = await self.get_by_id(score_id)
        if score:
            score.download_count += 1
            await self.session.flush()
