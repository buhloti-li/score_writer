import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.score import CopyrightType, ScoreStatus


class ScoreCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    title_en: str | None = Field(None, max_length=300)
    composer: str | None = Field(None, max_length=200)
    arranger: str | None = Field(None, max_length=200)
    lyricist: str | None = Field(None, max_length=200)
    instrument: str | None = Field(None, max_length=100)
    key_signature: str | None = Field(None, max_length=50)
    time_signature: str | None = Field(None, max_length=20)
    difficulty: int | None = Field(None, ge=1, le=5)
    genre: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    page_count: int | None = Field(None, ge=1)
    price: Decimal = Field(default=Decimal("0.00"), ge=0)
    description: str | None = None
    copyright_status: CopyrightType = CopyrightType.UNKNOWN
    original_source: str | None = None


class ScoreUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    title_en: str | None = None
    composer: str | None = None
    arranger: str | None = None
    lyricist: str | None = None
    instrument: str | None = None
    key_signature: str | None = None
    time_signature: str | None = None
    difficulty: int | None = Field(None, ge=1, le=5)
    genre: str | None = None
    tags: list[str] | None = None
    page_count: int | None = Field(None, ge=1)
    price: Decimal | None = Field(None, ge=0)
    status: ScoreStatus | None = None
    description: str | None = None
    copyright_status: CopyrightType | None = None


class ScoreResponse(BaseModel):
    id: uuid.UUID
    title: str
    title_en: str | None
    composer: str | None
    arranger: str | None
    lyricist: str | None
    instrument: str | None
    key_signature: str | None
    time_signature: str | None
    difficulty: int | None
    genre: str | None
    tags: list[str] | None
    page_count: int | None
    price: Decimal
    status: ScoreStatus
    preview_image_url: str | None
    pdf_watermarked_url: str | None
    copyright_status: CopyrightType
    download_count: int
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScoreListResponse(BaseModel):
    items: list[ScoreResponse]
    total: int
    page: int
    page_size: int
