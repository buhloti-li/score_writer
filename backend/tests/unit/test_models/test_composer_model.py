from app.models.composer import CopyrightStatus
from tests.conftest import create_test_composer


class TestComposerModel:
    """Composer model tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_composer(self, db_session):
        composer = await create_test_composer(db_session)
        assert composer.name_zh == "贝多芬"
        assert composer.name_en == "Beethoven"
        assert composer.death_year == 1827

    async def test_public_domain_classical(self, db_session):
        """Beethoven died 1827, clearly public domain in 2026."""
        composer = await create_test_composer(db_session, death_year=1827)
        assert composer.is_public_domain(2026) is True

    async def test_protected_modern(self, db_session):
        """Composer who died in 2000, still protected until 2050."""
        composer = await create_test_composer(
            db_session,
            name_zh="现代作曲家",
            name_en="Modern",
            death_year=2000,
            copyright_status=CopyrightStatus.PROTECTED,
        )
        assert composer.is_public_domain(2026) is False

    async def test_public_domain_by_status(self, db_session):
        """Even without death year, public domain status is respected."""
        composer = await create_test_composer(
            db_session,
            name_zh="古代",
            death_year=None,
            copyright_status=CopyrightStatus.PUBLIC_DOMAIN,
        )
        assert composer.is_public_domain(2026) is True

    # --- Boundary cases ---
    async def test_exactly_50_years_ago(self, db_session):
        """Died exactly 50 years before current year — NOT public domain yet.
        death_year + 50 = current_year means protection hasn't expired."""
        composer = await create_test_composer(
            db_session,
            name_zh="边界",
            death_year=1976,
            copyright_status=CopyrightStatus.UNKNOWN,
        )
        # 1976 + 50 = 2026, NOT < 2026, so NOT public domain
        assert composer.is_public_domain(2026) is False

    async def test_51_years_ago(self, db_session):
        """Died 51 years before current year — public domain."""
        composer = await create_test_composer(
            db_session,
            name_zh="刚过期",
            death_year=1975,
            copyright_status=CopyrightStatus.UNKNOWN,
        )
        # 1975 + 50 = 2025 < 2026
        assert composer.is_public_domain(2026) is True

    async def test_no_death_year_unknown_status(self, db_session):
        """No death year and unknown status — not public domain."""
        composer = await create_test_composer(
            db_session,
            name_zh="不详",
            death_year=None,
            copyright_status=CopyrightStatus.UNKNOWN,
        )
        assert composer.is_public_domain(2026) is False

    # --- Exception cases ---
    async def test_repr(self, db_session):
        composer = await create_test_composer(db_session)
        assert "贝多芬" in repr(composer)
        assert "Beethoven" in repr(composer)
