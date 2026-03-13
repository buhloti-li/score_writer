import uuid
from decimal import Decimal
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.score import CopyrightType, Score, ScoreStatus
from app.repositories.score_repo import ScoreRepository
from app.schemas.score import ScoreCreate, ScoreUpdate


class ScoreServiceError(Exception):
    pass


class ScoreService:
    def __init__(self, session: AsyncSession):
        self.repo = ScoreRepository(session)

    async def create_score(self, data: ScoreCreate) -> Score:
        return await self.repo.create(**data.model_dump())

    async def get_score(self, score_id: uuid.UUID) -> Score:
        score = await self.repo.get_by_id(score_id)
        if not score:
            raise ScoreServiceError("Score not found")
        return score

    async def update_score(self, score_id: uuid.UUID, data: ScoreUpdate) -> Score:
        score = await self.repo.get_by_id(score_id)
        if not score:
            raise ScoreServiceError("Score not found")
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return score
        updated = await self.repo.update_by_id(score_id, **update_data)
        return updated

    async def delete_score(self, score_id: uuid.UUID) -> bool:
        score = await self.repo.get_by_id(score_id)
        if not score:
            raise ScoreServiceError("Score not found")
        return await self.repo.delete_by_id(score_id)

    async def list_scores(
        self, offset: int = 0, limit: int = 20
    ) -> tuple[Sequence[Score], int]:
        scores = await self.repo.get_available(offset=offset, limit=limit)
        total = await self.repo.count(
            filters=[
                Score.status == ScoreStatus.AVAILABLE,
                Score.copyright_status.in_(
                    [CopyrightType.PUBLIC_DOMAIN, CopyrightType.LICENSED]
                ),
            ]
        )
        return scores, total

    async def list_by_instrument(
        self, instrument: str, offset: int = 0, limit: int = 20
    ) -> Sequence[Score]:
        return await self.repo.get_by_instrument(instrument, offset, limit)

    async def list_by_composer(
        self, composer: str, offset: int = 0, limit: int = 20
    ) -> Sequence[Score]:
        return await self.repo.get_by_composer(composer, offset, limit)

    async def list_by_price_range(
        self,
        min_price: Decimal,
        max_price: Decimal,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Score]:
        if min_price > max_price:
            raise ScoreServiceError("min_price must be <= max_price")
        return await self.repo.get_by_price_range(min_price, max_price, offset, limit)

    async def record_download(self, score_id: uuid.UUID) -> None:
        score = await self.repo.get_by_id(score_id)
        if not score:
            raise ScoreServiceError("Score not found")
        await self.repo.increment_download_count(score_id)

    async def search_scores(
        self,
        query: str = "",
        instrument: str | None = None,
        genre: str | None = None,
        difficulty: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Score], int]:
        filters = [
            Score.status == ScoreStatus.AVAILABLE,
        ]
        if query:
            filters.append(
                Score.title.ilike(f"%{query}%")
                | Score.title_en.ilike(f"%{query}%")
                | Score.composer.ilike(f"%{query}%")
            )
        if instrument:
            filters.append(Score.instrument == instrument)
        if genre:
            filters.append(Score.genre == genre)
        if difficulty:
            filters.append(Score.difficulty == difficulty)

        items = await self.repo.find_by(filters, offset, limit)
        total = await self.repo.count(filters)
        return items, total

    async def set_files(
        self,
        score_id: uuid.UUID,
        pdf_url: str | None = None,
        pdf_watermarked_url: str | None = None,
        lilypond_source_url: str | None = None,
        musicxml_url: str | None = None,
        preview_image_url: str | None = None,
        midi_url: str | None = None,
    ) -> Score:
        score = await self.repo.get_by_id(score_id)
        if not score:
            raise ScoreServiceError("Score not found")
        update_kwargs = {}
        if pdf_url is not None:
            update_kwargs["pdf_url"] = pdf_url
        if pdf_watermarked_url is not None:
            update_kwargs["pdf_watermarked_url"] = pdf_watermarked_url
        if lilypond_source_url is not None:
            update_kwargs["lilypond_source_url"] = lilypond_source_url
        if musicxml_url is not None:
            update_kwargs["musicxml_url"] = musicxml_url
        if preview_image_url is not None:
            update_kwargs["preview_image_url"] = preview_image_url
        if midi_url is not None:
            update_kwargs["midi_url"] = midi_url
        if update_kwargs:
            return await self.repo.update_by_id(score_id, **update_kwargs)
        return score
