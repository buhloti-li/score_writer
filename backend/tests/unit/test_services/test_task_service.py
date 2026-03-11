import uuid

import pytest

from app.models.task import TaskPriority, TaskStatus, TaskType
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService, TaskServiceError
from tests.conftest import create_test_task


class TestTaskService:
    """Task service tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_create_customer_task(self, db_session):
        service = TaskService(db_session)
        task = await service.create_task(
            TaskCreate(
                type=TaskType.CUSTOMER_TRANSCRIBE,
                title="月光奏鸣曲",
            )
        )
        assert task.type == TaskType.CUSTOMER_TRANSCRIBE
        assert task.priority == TaskPriority.HIGH  # auto-elevated
        assert task.deadline_at is not None  # auto-set to +1 day

    async def test_create_proactive_import(self, db_session):
        service = TaskService(db_session)
        task = await service.create_task(
            TaskCreate(
                type=TaskType.PROACTIVE_IMPORT,
                title="IMSLP Import",
            )
        )
        assert task.priority == TaskPriority.NORMAL
        assert task.deadline_at is None

    async def test_transition_status(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        service = TaskService(db_session)
        updated = await service.transition_status(task.id, TaskStatus.PROCESSING)
        assert updated.status == TaskStatus.PROCESSING

    async def test_approve_task(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.REVIEW)
        service = TaskService(db_session)
        approved = await service.approve_task(task.id, "Looks good")
        assert approved.status == TaskStatus.APPROVED
        assert approved.approved_at is not None
        assert approved.admin_notes == "Looks good"

    async def test_discard_task(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        service = TaskService(db_session)
        discarded = await service.discard_task(task.id)
        assert discarded.status == TaskStatus.DISCARDED

    async def test_assign_task(self, db_session):
        from tests.conftest import create_test_admin

        task = await create_test_task(db_session)
        admin = await create_test_admin(db_session)
        service = TaskService(db_session)
        assigned = await service.assign_task(task.id, admin.id)
        assert assigned.assigned_admin_id == admin.id

    async def test_list_by_type(self, db_session):
        await create_test_task(db_session, title="CT", task_type=TaskType.CUSTOMER_TRANSCRIBE)
        await create_test_task(db_session, title="PI", task_type=TaskType.PROACTIVE_IMPORT)
        service = TaskService(db_session)
        tasks, total = await service.list_by_type(TaskType.CUSTOMER_TRANSCRIBE)
        assert total == 1
        assert tasks[0].title == "CT"

    async def test_is_queue_idle_when_empty(self, db_session):
        service = TaskService(db_session)
        assert await service.is_queue_idle() is True

    async def test_is_queue_idle_when_busy(self, db_session):
        await create_test_task(
            db_session,
            task_type=TaskType.CUSTOMER_TRANSCRIBE,
            status=TaskStatus.PROCESSING,
        )
        service = TaskService(db_session)
        assert await service.is_queue_idle() is False

    # --- Boundary cases ---
    async def test_customer_task_auto_high_priority(self, db_session):
        """Customer tasks should auto-elevate to HIGH even if created as NORMAL."""
        service = TaskService(db_session)
        task = await service.create_task(
            TaskCreate(
                type=TaskType.CUSTOMER_TRANSCRIBE,
                title="Auto Priority",
                priority=TaskPriority.NORMAL,
            )
        )
        assert task.priority == TaskPriority.HIGH

    async def test_customer_task_keep_urgent(self, db_session):
        """URGENT should not be downgraded to HIGH."""
        service = TaskService(db_session)
        task = await service.create_task(
            TaskCreate(
                type=TaskType.CUSTOMER_TRANSCRIBE,
                title="Urgent Task",
                priority=TaskPriority.URGENT,
            )
        )
        assert task.priority == TaskPriority.URGENT

    async def test_update_task_empty(self, db_session):
        task = await create_test_task(db_session)
        service = TaskService(db_session)
        updated = await service.update_task(task.id, TaskUpdate())
        assert updated.title == task.title

    # --- Exception cases ---
    async def test_get_nonexistent(self, db_session):
        service = TaskService(db_session)
        with pytest.raises(TaskServiceError, match="Task not found"):
            await service.get_task(uuid.uuid4())

    async def test_invalid_transition(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        service = TaskService(db_session)
        with pytest.raises(TaskServiceError, match="Cannot transition"):
            await service.transition_status(task.id, TaskStatus.APPROVED)

    async def test_approve_non_review_task(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        service = TaskService(db_session)
        with pytest.raises(TaskServiceError, match="must be in review"):
            await service.approve_task(task.id)

    async def test_discard_delivered_task(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.DELIVERED)
        service = TaskService(db_session)
        with pytest.raises(TaskServiceError, match="terminal status"):
            await service.discard_task(task.id)

    async def test_update_with_invalid_transition(self, db_session):
        task = await create_test_task(db_session, status=TaskStatus.PENDING)
        service = TaskService(db_session)
        with pytest.raises(TaskServiceError, match="Cannot transition"):
            await service.update_task(task.id, TaskUpdate(status=TaskStatus.DELIVERED))
