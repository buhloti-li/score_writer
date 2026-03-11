import uuid
from decimal import Decimal

import pytest

from app.models.order import DeliveryStatus, PaymentStatus
from app.services.order_service import OrderService, OrderServiceError
from tests.conftest import create_test_order, create_test_score, create_test_user


class TestOrderService:
    """Order service tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_order_for_score(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session, price=Decimal("15.00"))
        service = OrderService(db_session)
        order = await service.create_order(user_id=user.id, score_id=score.id)
        assert order.user_id == user.id
        assert order.score_id == score.id
        assert order.amount == Decimal("15.00")

    async def test_get_order(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score)
        service = OrderService(db_session)
        fetched = await service.get_order(order.id)
        assert fetched.id == order.id

    async def test_get_user_orders(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        await create_test_order(db_session, user, score)
        service = OrderService(db_session)
        orders = await service.get_user_orders(user.id)
        assert len(orders) == 1

    async def test_mark_paid(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score)
        service = OrderService(db_session)
        paid = await service.mark_paid(order.id, "alipay")
        assert paid.payment_status == PaymentStatus.PAID
        assert paid.payment_method == "alipay"

    async def test_mark_delivered(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score, payment_status=PaymentStatus.PAID)
        service = OrderService(db_session)
        delivered = await service.mark_delivered(order.id)
        assert delivered.delivery_status == DeliveryStatus.DELIVERED
        assert delivered.delivered_at is not None

    async def test_refund(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score, payment_status=PaymentStatus.PAID)
        service = OrderService(db_session)
        refunded = await service.refund(order.id)
        assert refunded.payment_status == PaymentStatus.REFUNDED

    # --- Boundary cases ---
    async def test_create_order_custom_amount(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session, price=Decimal("10.00"))
        service = OrderService(db_session)
        order = await service.create_order(
            user_id=user.id, score_id=score.id, amount=Decimal("20.00")
        )
        assert order.amount == Decimal("20.00")

    # --- Exception cases ---
    async def test_create_order_no_score_no_task(self, db_session):
        user = await create_test_user(db_session)
        service = OrderService(db_session)
        with pytest.raises(OrderServiceError, match="Either score_id or task_id"):
            await service.create_order(user_id=user.id)

    async def test_create_order_nonexistent_score(self, db_session):
        user = await create_test_user(db_session)
        service = OrderService(db_session)
        with pytest.raises(OrderServiceError, match="Score not found"):
            await service.create_order(user_id=user.id, score_id=uuid.uuid4())

    async def test_create_order_unsellable_score(self, db_session):
        from app.models.score import ScoreStatus

        user = await create_test_user(db_session)
        score = await create_test_score(db_session, status=ScoreStatus.OFFLINE)
        service = OrderService(db_session)
        with pytest.raises(OrderServiceError, match="not available for sale"):
            await service.create_order(user_id=user.id, score_id=score.id)

    async def test_get_nonexistent_order(self, db_session):
        service = OrderService(db_session)
        with pytest.raises(OrderServiceError, match="Order not found"):
            await service.get_order(uuid.uuid4())

    async def test_mark_paid_already_paid(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score, payment_status=PaymentStatus.PAID)
        service = OrderService(db_session)
        with pytest.raises(OrderServiceError, match="not in pending"):
            await service.mark_paid(order.id, "alipay")

    async def test_deliver_unpaid_order(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score)
        service = OrderService(db_session)
        with pytest.raises(OrderServiceError, match="cannot be delivered"):
            await service.mark_delivered(order.id)

    async def test_refund_unpaid_order(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score)
        service = OrderService(db_session)
        with pytest.raises(OrderServiceError, match="Only paid orders"):
            await service.refund(order.id)
