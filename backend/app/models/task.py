import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import GUID, StringArray

from app.database import Base


class TaskType(str, enum.Enum):
    CUSTOMER_TRANSCRIBE = "customer_transcribe"
    PROACTIVE_IMPORT = "proactive_import"
    PROACTIVE_TRANSCRIBE = "proactive_transcribe"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELIVERED = "delivered"
    DISCARDED = "discarded"


class TaskPriority(str, enum.Enum):
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ImageSource(str, enum.Enum):
    USER_UPLOAD = "user_upload"
    WEB_CRAWL = "web_crawl"
    AUTO_CRAWL = "auto_crawl"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    type: Mapped[TaskType] = mapped_column(Enum(TaskType), index=True)
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("orders.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(300))
    source: Mapped[str | None] = mapped_column(String(50))
    customer_info: Mapped[dict | None] = mapped_column(JSON)
    original_images: Mapped[list[str] | None] = mapped_column(StringArray())
    original_file_url: Mapped[str | None] = mapped_column(String(500))
    image_source: Mapped[ImageSource | None] = mapped_column(Enum(ImageSource))
    crawl_source_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, index=True
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), default=TaskPriority.NORMAL, index=True
    )
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    score_metadata: Mapped[dict | None] = mapped_column(JSON)
    omr_result_json: Mapped[dict | None] = mapped_column(JSON)
    lilypond_source: Mapped[str | None] = mapped_column(Text)
    output_pdf_url: Mapped[str | None] = mapped_column(String(500))
    confidence_score: Mapped[float | None] = mapped_column(Float)
    assigned_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id"), index=True
    )
    admin_notes: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    assigned_admin: Mapped["User | None"] = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_admin_id])  # noqa: F821

    def is_customer_task(self) -> bool:
        return self.type == TaskType.CUSTOMER_TRANSCRIBE

    def is_overdue(self, now: datetime | None = None) -> bool:
        if self.deadline_at is None:
            return False
        check_time = now or datetime.now(self.deadline_at.tzinfo)
        return check_time > self.deadline_at

    def can_transition_to(self, new_status: TaskStatus) -> bool:
        allowed = {
            TaskStatus.PENDING: {TaskStatus.PROCESSING, TaskStatus.DISCARDED},
            TaskStatus.PROCESSING: {TaskStatus.REVIEW, TaskStatus.PENDING, TaskStatus.DISCARDED},
            TaskStatus.REVIEW: {TaskStatus.APPROVED, TaskStatus.REJECTED, TaskStatus.PROCESSING},
            TaskStatus.REJECTED: {TaskStatus.PROCESSING, TaskStatus.DISCARDED},
            TaskStatus.APPROVED: {TaskStatus.DELIVERED},
            TaskStatus.DELIVERED: set(),
            TaskStatus.DISCARDED: set(),
        }
        return new_status in allowed.get(self.status, set())

    def __repr__(self) -> str:
        return f"<Task {self.title} ({self.type.value}) [{self.status.value}]>"
