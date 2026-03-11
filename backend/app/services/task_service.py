import uuid
from datetime import datetime, timedelta, timezone
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskPriority, TaskStatus, TaskType
from app.repositories.task_repo import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskServiceError(Exception):
    pass


class TaskService:
    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def create_task(self, data: TaskCreate, order_id: uuid.UUID | None = None) -> Task:
        deadline_at = None
        priority = data.priority

        if data.type == TaskType.CUSTOMER_TRANSCRIBE:
            deadline_at = datetime.now(timezone.utc) + timedelta(days=1)
            if priority == TaskPriority.NORMAL:
                priority = TaskPriority.HIGH

        return await self.repo.create(
            type=data.type,
            order_id=order_id,
            title=data.title,
            source=data.source,
            customer_info=data.customer_info,
            original_images=data.original_images,
            original_file_url=data.original_file_url,
            image_source=data.image_source,
            crawl_source_url=data.crawl_source_url,
            priority=priority,
            deadline_at=deadline_at,
            score_metadata=data.score_metadata,
        )

    async def get_task(self, task_id: uuid.UUID) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise TaskServiceError("Task not found")
        return task

    async def update_task(self, task_id: uuid.UUID, data: TaskUpdate) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise TaskServiceError("Task not found")

        if data.status and not task.can_transition_to(data.status):
            raise TaskServiceError(
                f"Cannot transition from {task.status.value} to {data.status.value}"
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return task
        updated = await self.repo.update_by_id(task_id, **update_data)
        return updated

    async def transition_status(self, task_id: uuid.UUID, new_status: TaskStatus) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise TaskServiceError("Task not found")
        if not task.can_transition_to(new_status):
            raise TaskServiceError(
                f"Cannot transition from {task.status.value} to {new_status.value}"
            )
        kwargs = {"status": new_status}
        if new_status == TaskStatus.APPROVED:
            kwargs["approved_at"] = datetime.now(timezone.utc)
        return await self.repo.update_by_id(task_id, **kwargs)

    async def approve_task(self, task_id: uuid.UUID, admin_notes: str | None = None) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise TaskServiceError("Task not found")
        if task.status != TaskStatus.REVIEW:
            raise TaskServiceError("Task must be in review status to approve")
        return await self.repo.update_by_id(
            task_id,
            status=TaskStatus.APPROVED,
            approved_at=datetime.now(timezone.utc),
            admin_notes=admin_notes or task.admin_notes,
        )

    async def discard_task(self, task_id: uuid.UUID) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise TaskServiceError("Task not found")
        if task.status in (TaskStatus.DELIVERED, TaskStatus.DISCARDED):
            raise TaskServiceError("Task is already in terminal status")
        return await self.repo.update_by_id(task_id, status=TaskStatus.DISCARDED)

    async def assign_task(self, task_id: uuid.UUID, admin_id: uuid.UUID) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise TaskServiceError("Task not found")
        return await self.repo.update_by_id(task_id, assigned_admin_id=admin_id)

    async def list_by_type(
        self, task_type: TaskType, offset: int = 0, limit: int = 20
    ) -> tuple[Sequence[Task], int]:
        tasks = await self.repo.get_by_type(task_type, offset, limit)
        total = await self.repo.count(filters=[Task.type == task_type])
        return tasks, total

    async def list_customer_tasks(
        self, offset: int = 0, limit: int = 20
    ) -> Sequence[Task]:
        return await self.repo.get_customer_tasks_by_urgency(offset, limit)

    async def is_queue_idle(self) -> bool:
        count = await self.repo.count_pending_customer_tasks()
        return count == 0
