from app.models.task import TaskPriority, TaskStatus, TaskType
from app.repositories.task_repo import TaskRepository
from tests.conftest import create_test_task


class TestTaskRepository:
    """Task repository tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    async def test_get_by_type(self, db_session):
        await create_test_task(db_session, title="Customer 1", task_type=TaskType.CUSTOMER_TRANSCRIBE)
        await create_test_task(db_session, title="Import 1", task_type=TaskType.PROACTIVE_IMPORT)
        repo = TaskRepository(db_session)
        customer_tasks = await repo.get_by_type(TaskType.CUSTOMER_TRANSCRIBE)
        assert len(customer_tasks) == 1
        assert customer_tasks[0].title == "Customer 1"

    async def test_get_by_status(self, db_session):
        await create_test_task(db_session, title="Pending", status=TaskStatus.PENDING)
        await create_test_task(db_session, title="Review", status=TaskStatus.REVIEW)
        repo = TaskRepository(db_session)
        pending = await repo.get_by_status(TaskStatus.PENDING)
        assert len(pending) == 1

    async def test_get_customer_tasks_by_urgency(self, db_session):
        await create_test_task(
            db_session,
            title="Customer Task",
            task_type=TaskType.CUSTOMER_TRANSCRIBE,
            status=TaskStatus.PENDING,
        )
        await create_test_task(
            db_session,
            title="Proactive Task",
            task_type=TaskType.PROACTIVE_IMPORT,
            status=TaskStatus.PENDING,
        )
        repo = TaskRepository(db_session)
        urgent = await repo.get_customer_tasks_by_urgency()
        assert len(urgent) == 1
        assert urgent[0].title == "Customer Task"

    async def test_count_pending_customer_tasks(self, db_session):
        await create_test_task(
            db_session,
            title="T1",
            task_type=TaskType.CUSTOMER_TRANSCRIBE,
            status=TaskStatus.PENDING,
        )
        await create_test_task(
            db_session,
            title="T2",
            task_type=TaskType.CUSTOMER_TRANSCRIBE,
            status=TaskStatus.PROCESSING,
        )
        await create_test_task(
            db_session,
            title="T3",
            task_type=TaskType.CUSTOMER_TRANSCRIBE,
            status=TaskStatus.DELIVERED,
        )
        repo = TaskRepository(db_session)
        count = await repo.count_pending_customer_tasks()
        assert count == 2  # pending + processing, not delivered

    # --- Boundary cases ---
    async def test_empty_results(self, db_session):
        repo = TaskRepository(db_session)
        tasks = await repo.get_by_type(TaskType.PROACTIVE_TRANSCRIBE)
        assert len(tasks) == 0

    async def test_count_by_type_and_status(self, db_session):
        await create_test_task(
            db_session,
            title="PI1",
            task_type=TaskType.PROACTIVE_IMPORT,
            status=TaskStatus.PENDING,
        )
        repo = TaskRepository(db_session)
        count = await repo.count_by_type_and_status(TaskType.PROACTIVE_IMPORT, TaskStatus.PENDING)
        assert count == 1
        count2 = await repo.count_by_type_and_status(TaskType.PROACTIVE_IMPORT, TaskStatus.REVIEW)
        assert count2 == 0

    # --- Delivered/discarded excluded from urgency ---
    async def test_delivered_excluded_from_urgency(self, db_session):
        await create_test_task(
            db_session,
            title="Delivered",
            task_type=TaskType.CUSTOMER_TRANSCRIBE,
            status=TaskStatus.DELIVERED,
        )
        repo = TaskRepository(db_session)
        urgent = await repo.get_customer_tasks_by_urgency()
        assert len(urgent) == 0
