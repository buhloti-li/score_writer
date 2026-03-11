import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import GUID, StringArray

from app.database import Base


class ScoreStatus(str, enum.Enum):
    AVAILABLE = "available"
    PRODUCING = "producing"
    OFFLINE = "offline"


class CopyrightType(str, enum.Enum):
    PUBLIC_DOMAIN = "public_domain"
    LICENSED = "licensed"
    USER_ONLY = "user_only"
    UNKNOWN = "unknown"


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(300), index=True)
    title_en: Mapped[str | None] = mapped_column(String(300), index=True)
    composer: Mapped[str | None] = mapped_column(String(200), index=True)
    arranger: Mapped[str | None] = mapped_column(String(200))
    lyricist: Mapped[str | None] = mapped_column(String(200))
    instrument: Mapped[str | None] = mapped_column(String(100), index=True)
    key_signature: Mapped[str | None] = mapped_column(String(50))
    time_signature: Mapped[str | None] = mapped_column(String(20))
    difficulty: Mapped[int | None] = mapped_column(Integer)
    genre: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[list[str] | None] = mapped_column(StringArray())
    page_count: Mapped[int | None] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    status: Mapped[ScoreStatus] = mapped_column(
        Enum(ScoreStatus), default=ScoreStatus.AVAILABLE, index=True
    )
    # File URLs
    lilypond_source_url: Mapped[str | None] = mapped_column(String(500))
    pdf_url: Mapped[str | None] = mapped_column(String(500))
    pdf_watermarked_url: Mapped[str | None] = mapped_column(String(500))
    preview_image_url: Mapped[str | None] = mapped_column(String(500))
    musicxml_url: Mapped[str | None] = mapped_column(String(500))
    midi_url: Mapped[str | None] = mapped_column(String(500))
    # Copyright
    copyright_status: Mapped[CopyrightType] = mapped_column(
        Enum(CopyrightType), default=CopyrightType.UNKNOWN
    )
    original_source: Mapped[str | None] = mapped_column(String(500))
    # Stats
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text)
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="score", foreign_keys="[Order.score_id]")  # noqa: F821

    def is_sellable(self) -> bool:
        return (
            self.status == ScoreStatus.AVAILABLE
            and self.copyright_status
            in (CopyrightType.PUBLIC_DOMAIN, CopyrightType.LICENSED)
            and self.pdf_url is not None
        )

    def __repr__(self) -> str:
        return f"<Score {self.title}>"
