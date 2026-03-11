import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.order import DeliveryStatus, OrderSource, PaymentStatus


class OrderCreate(BaseModel):
    score_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    source: OrderSource = OrderSource.WEBSITE
    amount: Decimal = Field(ge=0)
    payment_method: str | None = None


class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    score_id: uuid.UUID | None
    task_id: uuid.UUID | None
    source: OrderSource
    amount: Decimal
    payment_method: str | None
    payment_status: PaymentStatus
    delivery_status: DeliveryStatus
    delivered_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int


class PaymentCallback(BaseModel):
    order_id: uuid.UUID
    payment_method: str
    transaction_id: str
    status: str
