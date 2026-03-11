import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.types import GUID

from app.database import Base


class OrderSource(str, enum.Enum):
    TAOBAO = "taobao"
    WEBSITE = "website"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"


class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    DELIVERED = "delivered"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id"), index=True
    )
    score_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("scores.id"), index=True
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("tasks.id", use_alter=True), index=True
    )
    source: Mapped[OrderSource] = mapped_column(Enum(OrderSource), default=OrderSource.WEBSITE)
    taobao_order_id: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    payment_method: Mapped[str | None] = mapped_column(String(50))
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING, index=True
    )
    delivery_status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus), default=DeliveryStatus.PENDING
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User | None"] = relationship("User", back_populates="orders", foreign_keys=[user_id])  # noqa: F821
    score: Mapped["Score | None"] = relationship("Score", back_populates="orders", foreign_keys=[score_id])  # noqa: F821

    def can_deliver(self) -> bool:
        return (
            self.payment_status == PaymentStatus.PAID
            and self.delivery_status == DeliveryStatus.PENDING
        )

    def __repr__(self) -> str:
        return f"<Order {self.id} status={self.payment_status.value}>"
