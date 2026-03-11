from decimal import Decimal

from app.models.score import CopyrightType, ScoreStatus
from tests.conftest import create_test_score


class TestScoreModel:
    """Score model tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_score(self, db_session):
        score = await create_test_score(db_session)
        assert score.title == "Für Elise"
        assert score.composer == "Beethoven"
        assert score.price == Decimal("10.00")

    async def test_sellable_public_domain(self, db_session):
        score = await create_test_score(
            db_session,
            status=ScoreStatus.AVAILABLE,
            copyright_status=CopyrightType.PUBLIC_DOMAIN,
            pdf_url="https://example.com/test.pdf",
        )
        assert score.is_sellable() is True

    async def test_sellable_licensed(self, db_session):
        score = await create_test_score(
            db_session,
            copyright_status=CopyrightType.LICENSED,
        )
        assert score.is_sellable() is True

    # --- Boundary cases ---
    async def test_not_sellable_no_pdf(self, db_session):
        score = await create_test_score(db_session, pdf_url=None)
        assert score.is_sellable() is False

    async def test_not_sellable_offline(self, db_session):
        score = await create_test_score(db_session, status=ScoreStatus.OFFLINE)
        assert score.is_sellable() is False

    async def test_not_sellable_user_only(self, db_session):
        score = await create_test_score(
            db_session, copyright_status=CopyrightType.USER_ONLY
        )
        assert score.is_sellable() is False

    async def test_not_sellable_unknown_copyright(self, db_session):
        score = await create_test_score(
            db_session, copyright_status=CopyrightType.UNKNOWN
        )
        assert score.is_sellable() is False

    async def test_not_sellable_producing(self, db_session):
        score = await create_test_score(db_session, status=ScoreStatus.PRODUCING)
        assert score.is_sellable() is False

    async def test_zero_price_score(self, db_session):
        score = await create_test_score(db_session, price=Decimal("0.00"))
        assert score.price == Decimal("0.00")
        assert score.is_sellable() is True

    async def test_default_download_count(self, db_session):
        score = await create_test_score(db_session)
        assert score.download_count == 0

    # --- Exception cases ---
    async def test_repr(self, db_session):
        score = await create_test_score(db_session)
        assert "Für Elise" in repr(score)
