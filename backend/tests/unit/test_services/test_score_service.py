import uuid
from decimal import Decimal

import pytest

from app.models.score import ScoreStatus
from app.schemas.score import ScoreCreate, ScoreUpdate
from app.services.score_service import ScoreService, ScoreServiceError
from tests.conftest import create_test_score


class TestScoreService:
    """Score service tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_score(self, db_session):
        service = ScoreService(db_session)
        score = await service.create_score(
            ScoreCreate(title="New Score", composer="Bach", price=Decimal("15.00"))
        )
        assert score.title == "New Score"

    async def test_get_score(self, db_session):
        test_score = await create_test_score(db_session)
        service = ScoreService(db_session)
        score = await service.get_score(test_score.id)
        assert score.title == test_score.title

    async def test_update_score(self, db_session):
        test_score = await create_test_score(db_session)
        service = ScoreService(db_session)
        updated = await service.update_score(
            test_score.id,
            ScoreUpdate(title="Updated Title"),
        )
        assert updated.title == "Updated Title"

    async def test_delete_score(self, db_session):
        test_score = await create_test_score(db_session)
        service = ScoreService(db_session)
        result = await service.delete_score(test_score.id)
        assert result is True

    async def test_list_scores(self, db_session):
        await create_test_score(db_session, title="S1")
        await create_test_score(db_session, title="S2", price=Decimal("20.00"))
        service = ScoreService(db_session)
        scores, total = await service.list_scores()
        assert total == 2

    async def test_list_by_instrument(self, db_session):
        await create_test_score(db_session)  # default instrument=piano
        service = ScoreService(db_session)
        results = await service.list_by_instrument("piano")
        assert len(results) >= 1

    async def test_list_by_price_range(self, db_session):
        await create_test_score(db_session, title="Cheap", price=Decimal("5.00"))
        await create_test_score(db_session, title="Mid", price=Decimal("15.00"))
        await create_test_score(db_session, title="Expensive", price=Decimal("100.00"))
        service = ScoreService(db_session)
        results = await service.list_by_price_range(Decimal("1.00"), Decimal("20.00"))
        assert all(s.price <= Decimal("20.00") for s in results)

    async def test_record_download(self, db_session):
        test_score = await create_test_score(db_session)
        service = ScoreService(db_session)
        await service.record_download(test_score.id)
        score = await service.get_score(test_score.id)
        assert score.download_count == 1

    async def test_set_files(self, db_session):
        test_score = await create_test_score(db_session)
        service = ScoreService(db_session)
        updated = await service.set_files(
            test_score.id,
            pdf_url="https://example.com/new.pdf",
            preview_image_url="https://example.com/preview.png",
        )
        assert updated.pdf_url == "https://example.com/new.pdf"
        assert updated.preview_image_url == "https://example.com/preview.png"

    # --- Boundary cases ---
    async def test_update_with_no_changes(self, db_session):
        test_score = await create_test_score(db_session)
        service = ScoreService(db_session)
        updated = await service.update_score(test_score.id, ScoreUpdate())
        assert updated.title == test_score.title

    async def test_list_empty(self, db_session):
        service = ScoreService(db_session)
        scores, total = await service.list_scores()
        assert total == 0
        assert len(scores) == 0

    # --- Exception cases ---
    async def test_get_nonexistent(self, db_session):
        service = ScoreService(db_session)
        with pytest.raises(ScoreServiceError, match="Score not found"):
            await service.get_score(uuid.uuid4())

    async def test_update_nonexistent(self, db_session):
        service = ScoreService(db_session)
        with pytest.raises(ScoreServiceError, match="Score not found"):
            await service.update_score(uuid.uuid4(), ScoreUpdate(title="X"))

    async def test_delete_nonexistent(self, db_session):
        service = ScoreService(db_session)
        with pytest.raises(ScoreServiceError, match="Score not found"):
            await service.delete_score(uuid.uuid4())

    async def test_price_range_invalid(self, db_session):
        service = ScoreService(db_session)
        with pytest.raises(ScoreServiceError, match="min_price must be <= max_price"):
            await service.list_by_price_range(Decimal("100.00"), Decimal("1.00"))

    async def test_record_download_nonexistent(self, db_session):
        service = ScoreService(db_session)
        with pytest.raises(ScoreServiceError, match="Score not found"):
            await service.record_download(uuid.uuid4())
