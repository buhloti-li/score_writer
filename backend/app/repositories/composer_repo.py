from typing import Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.composer import Composer, CopyrightStatus
from app.repositories.base import BaseRepository


class ComposerRepository(BaseRepository[Composer]):
    def __init__(self, session: AsyncSession):
        super().__init__(Composer, session)

    async def get_by_name(self, name: str) -> Composer | None:
        result = await self.session.execute(
            select(Composer).where(
                or_(Composer.name_zh == name, Composer.name_en == name)
            )
        )
        return result.scalar_one_or_none()

    async def search_by_name(self, query: str) -> Sequence[Composer]:
        result = await self.session.execute(
            select(Composer).where(
                or_(
                    Composer.name_zh.ilike(f"%{query}%"),
                    Composer.name_en.ilike(f"%{query}%"),
                )
            )
        )
        return result.scalars().all()

    async def get_public_domain(self) -> Sequence[Composer]:
        result = await self.session.execute(
            select(Composer).where(
                Composer.copyright_status == CopyrightStatus.PUBLIC_DOMAIN
            )
        )
        return result.scalars().all()

    async def check_copyright(self, name: str, current_year: int = 2026) -> CopyrightStatus:
        composer = await self.get_by_name(name)
        if composer is None:
            return CopyrightStatus.UNKNOWN
        if composer.is_public_domain(current_year):
            return CopyrightStatus.PUBLIC_DOMAIN
        return composer.copyright_status
