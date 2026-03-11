from app.models.composer import CopyrightStatus
from app.repositories.composer_repo import ComposerRepository
from tests.conftest import create_test_composer


class TestComposerRepository:
    """Composer repository tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_get_by_name_zh(self, db_session):
        await create_test_composer(db_session, name_zh="莫扎特", name_en="Mozart", death_year=1791)
        repo = ComposerRepository(db_session)
        result = await repo.get_by_name("莫扎特")
        assert result is not None
        assert result.name_en == "Mozart"

    async def test_get_by_name_en(self, db_session):
        await create_test_composer(db_session, name_zh="巴赫", name_en="Bach", death_year=1750)
        repo = ComposerRepository(db_session)
        result = await repo.get_by_name("Bach")
        assert result is not None

    async def test_search_by_name(self, db_session):
        await create_test_composer(db_session, name_zh="贝多芬", name_en="Beethoven")
        repo = ComposerRepository(db_session)
        results = await repo.search_by_name("贝多")
        assert len(results) == 1

    async def test_get_public_domain(self, db_session):
        await create_test_composer(
            db_session,
            name_zh="PD",
            name_en="PublicDomain",
            copyright_status=CopyrightStatus.PUBLIC_DOMAIN,
        )
        await create_test_composer(
            db_session,
            name_zh="Protected",
            name_en="ProtectedOne",
            copyright_status=CopyrightStatus.PROTECTED,
        )
        repo = ComposerRepository(db_session)
        results = await repo.get_public_domain()
        assert len(results) == 1
        assert results[0].name_zh == "PD"

    async def test_check_copyright_public_domain(self, db_session):
        await create_test_composer(db_session, name_zh="贝多芬", death_year=1827)
        repo = ComposerRepository(db_session)
        status = await repo.check_copyright("贝多芬", 2026)
        assert status == CopyrightStatus.PUBLIC_DOMAIN

    # --- Boundary cases ---
    async def test_check_copyright_unknown_composer(self, db_session):
        repo = ComposerRepository(db_session)
        status = await repo.check_copyright("UnknownPerson", 2026)
        assert status == CopyrightStatus.UNKNOWN

    async def test_search_empty_results(self, db_session):
        repo = ComposerRepository(db_session)
        results = await repo.search_by_name("不存在的作曲家")
        assert len(results) == 0

    # --- Exception cases ---
    async def test_get_nonexistent_name(self, db_session):
        repo = ComposerRepository(db_session)
        result = await repo.get_by_name("Nobody")
        assert result is None
