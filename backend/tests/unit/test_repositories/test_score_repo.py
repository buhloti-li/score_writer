import uuid
from decimal import Decimal

import pytest

from app.models.score import CopyrightType, ScoreStatus
from app.repositories.score_repo import ScoreRepository
from tests.conftest import create_test_score


class TestScoreRepository:
    """Score repository tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_and_get(self, db_session):
        repo = ScoreRepository(db_session)
        score = await repo.create(
            title="Test Score",
            composer="Bach",
            price=Decimal("15.00"),
            status=ScoreStatus.AVAILABLE,
            copyright_status=CopyrightType.PUBLIC_DOMAIN,
            pdf_url="https://example.com/test.pdf",
        )
        assert score.id is not None
        fetched = await repo.get_by_id(score.id)
        assert fetched.title == "Test Score"

    async def test_get_available(self, db_session):
        await create_test_score(db_session, title="Available", status=ScoreStatus.AVAILABLE)
        await create_test_score(
            db_session, title="Offline", status=ScoreStatus.OFFLINE, price=Decimal("5.00")
        )
        repo = ScoreRepository(db_session)
        available = await repo.get_available()
        assert all(s.status == ScoreStatus.AVAILABLE for s in available)

    async def test_get_by_instrument(self, db_session):
        score = await create_test_score(db_session)
        repo = ScoreRepository(db_session)
        results = await repo.get_by_instrument("piano")
        assert len(results) >= 1

    async def test_get_by_composer(self, db_session):
        await create_test_score(db_session, composer="Mozart")
        repo = ScoreRepository(db_session)
        results = await repo.get_by_composer("Mozart")
        assert len(results) == 1
        assert results[0].composer == "Mozart"

    async def test_get_by_price_range(self, db_session):
        await create_test_score(db_session, title="Cheap", price=Decimal("5.00"))
        await create_test_score(db_session, title="Expensive", price=Decimal("50.00"))
        repo = ScoreRepository(db_session)
        results = await repo.get_by_price_range(Decimal("1.00"), Decimal("10.00"))
        assert all(Decimal("1.00") <= s.price <= Decimal("10.00") for s in results)

    async def test_increment_download_count(self, db_session):
        score = await create_test_score(db_session)
        repo = ScoreRepository(db_session)
        assert score.download_count == 0
        await repo.increment_download_count(score.id)
        updated = await repo.get_by_id(score.id)
        assert updated.download_count == 1

    # --- Boundary cases ---
    async def test_get_available_empty(self, db_session):
        repo = ScoreRepository(db_session)
        results = await repo.get_available()
        assert len(results) == 0

    async def test_pagination(self, db_session):
        for i in range(5):
            await create_test_score(db_session, title=f"Score {i}", price=Decimal(str(i + 1)))
        repo = ScoreRepository(db_session)
        page1 = await repo.get_available(offset=0, limit=2)
        page2 = await repo.get_available(offset=2, limit=2)
        assert len(page1) == 2
        assert len(page2) == 2

    async def test_count(self, db_session):
        await create_test_score(db_session, title="S1")
        await create_test_score(db_session, title="S2", price=Decimal("20.00"))
        repo = ScoreRepository(db_session)
        total = await repo.count()
        assert total == 2

    # --- Exception cases ---
    async def test_get_nonexistent(self, db_session):
        repo = ScoreRepository(db_session)
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None

    async def test_delete(self, db_session):
        score = await create_test_score(db_session)
        repo = ScoreRepository(db_session)
        deleted = await repo.delete_by_id(score.id)
        assert deleted is True
        assert await repo.get_by_id(score.id) is None

    async def test_delete_nonexistent(self, db_session):
        repo = ScoreRepository(db_session)
        deleted = await repo.delete_by_id(uuid.uuid4())
        assert deleted is False
