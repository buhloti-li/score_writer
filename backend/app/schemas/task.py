import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.task import ImageSource, TaskPriority, TaskStatus, TaskType


class TaskCreate(BaseModel):
    type: TaskType
    title: str = Field(min_length=1, max_length=300)
    source: str | None = None
    customer_info: dict | None = None
    original_images: list[str] | None = None
    original_file_url: str | None = None
    image_source: ImageSource | None = None
    crawl_source_url: str | None = None
    priority: TaskPriority = TaskPriority.NORMAL
    score_metadata: dict | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_admin_id: uuid.UUID | None = None
    admin_notes: str | None = None
    score_metadata: dict | None = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    type: TaskType
    order_id: uuid.UUID | None
    title: str
    source: str | None
    status: TaskStatus
    priority: TaskPriority
    deadline_at: datetime | None
    confidence_score: float | None
    assigned_admin_id: uuid.UUID | None
    admin_notes: str | None
    output_pdf_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int


class TaskApproveRequest(BaseModel):
    admin_notes: str | None = None
    score_metadata: dict | None = None
