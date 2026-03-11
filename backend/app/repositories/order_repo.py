import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import DeliveryStatus, Order, PaymentStatus
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_user(
        self, user_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_pending_delivery(self) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.payment_status == PaymentStatus.PAID)
            .where(Order.delivery_status == DeliveryStatus.PENDING)
            .order_by(Order.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_taobao_order_id(self, taobao_order_id: str) -> Order | None:
        result = await self.session.execute(
            select(Order).where(Order.taobao_order_id == taobao_order_id)
        )
        return result.scalar_one_or_none()
