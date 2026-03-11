import uuid
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskPriority, TaskStatus, TaskType
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_by_type(
        self, task_type: TaskType, offset: int = 0, limit: int = 20
    ) -> Sequence[Task]:
        stmt = (
            select(Task)
            .where(Task.type == task_type)
            .order_by(Task.priority.desc(), Task.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_status(
        self, status: TaskStatus, offset: int = 0, limit: int = 20
    ) -> Sequence[Task]:
        stmt = (
            select(Task)
            .where(Task.status == status)
            .order_by(Task.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_customer_tasks_by_urgency(
        self, offset: int = 0, limit: int = 20
    ) -> Sequence[Task]:
        stmt = (
            select(Task)
            .where(Task.type == TaskType.CUSTOMER_TRANSCRIBE)
            .where(Task.status.notin_([TaskStatus.DELIVERED, TaskStatus.DISCARDED]))
            .order_by(Task.deadline_at.asc().nullslast(), Task.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_assigned_to(
        self, admin_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> Sequence[Task]:
        stmt = (
            select(Task)
            .where(Task.assigned_admin_id == admin_id)
            .where(Task.status.notin_([TaskStatus.DELIVERED, TaskStatus.DISCARDED]))
            .order_by(Task.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_pending_customer_tasks(self) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Task)
            .where(Task.type == TaskType.CUSTOMER_TRANSCRIBE)
            .where(Task.status.in_([TaskStatus.PENDING, TaskStatus.PROCESSING]))
        )
        return result.scalar_one()

    async def count_by_type_and_status(
        self, task_type: TaskType, status: TaskStatus
    ) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Task)
            .where(Task.type == task_type)
            .where(Task.status == status)
        )
        return result.scalar_one()
