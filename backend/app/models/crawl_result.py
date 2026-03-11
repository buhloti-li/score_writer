import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.types import GUID

from app.database import Base


class CrawlResult(Base):
    __tablename__ = "crawl_results"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    query: Mapped[str] = mapped_column(String(300), index=True)
    source_url: Mapped[str] = mapped_column(String(500))
    original_image_url: Mapped[str | None] = mapped_column(String(500))
    watermarked_image_url: Mapped[str | None] = mapped_column(String(500))
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("tasks.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        check_time = now or datetime.now(self.expires_at.tzinfo)
        return check_time > self.expires_at

    def __repr__(self) -> str:
        return f"<CrawlResult query={self.query}>"
