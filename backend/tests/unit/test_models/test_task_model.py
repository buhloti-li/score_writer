from datetime import datetime, timedelta, timezone

from app.models.task import TaskPriority, TaskStatus, TaskType
from tests.conftest import create_test_task


class TestTaskModel:
    """Task model tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_task(self, db_session):
        task = await create_test_task(db_session)
        assert task.title == "Test Task"
        assert task.type == TaskType.CUSTOMER_TRANSCRIBE

    async def test_is_customer_task(self, db_session):
        task = await create_test_task(db_session, task_type=TaskType.CUSTOMER_TRANSCRIBE)
        assert task.is_customer_task() is True

    async def test_not_customer_task(self, db_session):
        task = await create_test_task(db_session, task_type=TaskType.PROACTIVE_IMPORT)
        assert task.is_customer_task() is False

    # --- Status transitions (normal) ---
    async def test_pending_to_processing(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        assert task.can_transition_to(TaskStatus.PROCESSING) is True

    async def test_processing_to_review(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PROCESSING)
        assert task.can_transition_to(TaskStatus.REVIEW) is True

    async def test_review_to_approved(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.REVIEW)
        assert task.can_transition_to(TaskStatus.APPROVED) is True

    async def test_approved_to_delivered(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.APPROVED)
        assert task.can_transition_to(TaskStatus.DELIVERED) is True

    # --- Status transitions (invalid) ---
    async def test_pending_cannot_go_to_approved(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        assert task.can_transition_to(TaskStatus.APPROVED) is False

    async def test_delivered_is_terminal(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.DELIVERED)
        assert task.can_transition_to(TaskStatus.PROCESSING) is False
        assert task.can_transition_to(TaskStatus.PENDING) is False

    async def test_discarded_is_terminal(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.DISCARDED)
        assert task.can_transition_to(TaskStatus.PROCESSING) is False

    # --- Overdue logic ---
    async def test_not_overdue_when_no_deadline(self, db_session):
        task = await create_test_task(db_session)
        task.deadline_at = None
        assert task.is_overdue() is False

    async def test_overdue_past_deadline(self, db_session):
        task = await create_test_task(db_session)
        task.deadline_at = datetime.now(timezone.utc) - timedelta(hours=1)
        assert task.is_overdue() is True

    async def test_not_overdue_future_deadline(self, db_session):
        task = await create_test_task(db_session)
        task.deadline_at = datetime.now(timezone.utc) + timedelta(hours=1)
        assert task.is_overdue() is False

    # --- Boundary: exactly at deadline ---
    async def test_overdue_exactly_at_deadline(self, db_session):
        now = datetime.now(timezone.utc)
        task = await create_test_task(db_session)
        task.deadline_at = now
        # now > now is False (not strictly overdue at exact time)
        result = task.is_overdue(now)
        assert result is False

    async def test_overdue_one_second_past(self, db_session):
        now = datetime.now(timezone.utc)
        task = await create_test_task(db_session)
        task.deadline_at = now - timedelta(seconds=1)
        assert task.is_overdue(now) is True

    # --- Discard transitions ---
    async def test_pending_can_discard(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        assert task.can_transition_to(TaskStatus.DISCARDED) is True

    async def test_processing_can_discard(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PROCESSING)
        assert task.can_transition_to(TaskStatus.DISCARDED) is True

    async def test_review_cannot_discard_directly(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.REVIEW)
        # review can go to processing or approved/rejected, not directly discard
        assert task.can_transition_to(TaskStatus.DISCARDED) is False
