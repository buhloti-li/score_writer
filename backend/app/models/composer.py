import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.types import GUID, StringArray

from app.database import Base


class CopyrightStatus(str, enum.Enum):
    PUBLIC_DOMAIN = "public_domain"
    PROTECTED = "protected"
    UNKNOWN = "unknown"


class Composer(Base):
    __tablename__ = "composers"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    name_zh: Mapped[str] = mapped_column(String(200), index=True)
    name_en: Mapped[str | None] = mapped_column(String(200), index=True)
    name_aliases: Mapped[list[str] | None] = mapped_column(StringArray())
    birth_year: Mapped[int | None] = mapped_column(Integer)
    death_year: Mapped[int | None] = mapped_column(Integer)
    nationality: Mapped[str | None] = mapped_column(String(100))
    copyright_status: Mapped[CopyrightStatus] = mapped_column(
        Enum(CopyrightStatus), default=CopyrightStatus.UNKNOWN
    )
    copyright_note: Mapped[str | None] = mapped_column(Text)
    imslp_url: Mapped[str | None] = mapped_column(String(500))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def is_public_domain(self, current_year: int = 2026) -> bool:
        if self.copyright_status == CopyrightStatus.PUBLIC_DOMAIN:
            return True
        if self.death_year is not None and (self.death_year + 50) < current_year:
            return True
        return False

    def __repr__(self) -> str:
        return f"<Composer {self.name_zh} ({self.name_en})>"
