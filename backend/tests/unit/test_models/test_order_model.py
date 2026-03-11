from app.models.order import DeliveryStatus, PaymentStatus
from tests.conftest import create_test_order, create_test_score, create_test_user


class TestOrderModel:
    """Order model tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_order(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score)
        assert order.user_id == user.id
        assert order.score_id == score.id
        assert order.payment_status == PaymentStatus.PENDING

    async def test_can_deliver_paid_pending(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score, payment_status=PaymentStatus.PAID)
        assert order.can_deliver() is True

    # --- Boundary cases ---
    async def test_cannot_deliver_not_paid(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score, payment_status=PaymentStatus.PENDING)
        assert order.can_deliver() is False

    async def test_cannot_deliver_already_delivered(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score, payment_status=PaymentStatus.PAID)
        order.delivery_status = DeliveryStatus.DELIVERED
        assert order.can_deliver() is False

    async def test_cannot_deliver_refunded(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(
            db_session, user, score, payment_status=PaymentStatus.REFUNDED
        )
        assert order.can_deliver() is False

    # --- Exception cases ---
    async def test_repr(self, db_session):
        user = await create_test_user(db_session)
        score = await create_test_score(db_session)
        order = await create_test_order(db_session, user, score)
        assert "pending" in repr(order)
