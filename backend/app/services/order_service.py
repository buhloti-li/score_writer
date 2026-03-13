import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import DeliveryStatus, Order, PaymentStatus
from app.repositories.order_repo import OrderRepository
from app.repositories.score_repo import ScoreRepository


class OrderServiceError(Exception):
    pass


class OrderService:
    def __init__(self, session: AsyncSession):
        self.order_repo = OrderRepository(session)
        self.score_repo = ScoreRepository(session)

    async def create_order(
        self,
        user_id: uuid.UUID,
        score_id: uuid.UUID | None = None,
        task_id: uuid.UUID | None = None,
        amount: Decimal = Decimal("0.00"),
        source: str = "website",
        payment_method: str | None = None,
    ) -> Order:
        if not score_id and not task_id:
            raise OrderServiceError("Either score_id or task_id is required")
        if score_id:
            score = await self.score_repo.get_by_id(score_id)
            if not score:
                raise OrderServiceError("Score not found")
            if not score.is_sellable():
                raise OrderServiceError("Score is not available for sale")
            if amount <= 0:
                amount = score.price

        return await self.order_repo.create(
            user_id=user_id,
            score_id=score_id,
            task_id=task_id,
            amount=amount,
            source=source,
            payment_method=payment_method,
        )

    async def get_order(self, order_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderServiceError("Order not found")
        return order

    async def get_user_orders(
        self, user_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> Sequence[Order]:
        return await self.order_repo.get_by_user(user_id, offset, limit)

    async def mark_paid(
        self, order_id: uuid.UUID, payment_method: str
    ) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderServiceError("Order not found")
        if order.payment_status != PaymentStatus.PENDING:
            raise OrderServiceError("Order is not in pending status")
        updated = await self.order_repo.update_by_id(
            order_id,
            payment_status=PaymentStatus.PAID,
            payment_method=payment_method,
        )
        return updated

    async def mark_delivered(self, order_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderServiceError("Order not found")
        if not order.can_deliver():
            raise OrderServiceError("Order cannot be delivered")
        updated = await self.order_repo.update_by_id(
            order_id,
            delivery_status=DeliveryStatus.DELIVERED,
            delivered_at=datetime.now(timezone.utc),
        )
        return updated

    async def list_all_orders(
        self, offset: int = 0, limit: int = 20
    ) -> Sequence[Order]:
        return await self.order_repo.get_all(offset=offset, limit=limit)

    async def refund(self, order_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderServiceError("Order not found")
        if order.payment_status != PaymentStatus.PAID:
            raise OrderServiceError("Only paid orders can be refunded")
        updated = await self.order_repo.update_by_id(
            order_id,
            payment_status=PaymentStatus.REFUNDED,
        )
        return updated
