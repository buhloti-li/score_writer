import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_admin_user
from app.models.task import TaskType
from app.models.user import User
from app.schemas.task import (
    TaskApproveRequest,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import TaskService, TaskServiceError

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    task_type: TaskType | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = TaskService(session)
    offset = (page - 1) * page_size

    if task_type:
        items, total = await service.list_by_type(task_type, offset, page_size)
    else:
        items = await service.list_customer_tasks(offset, page_size)
        total = len(items)

    return TaskListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = TaskService(session)
    try:
        return await service.get_task(task_id)
    except TaskServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = TaskService(session)
    return await service.create_task(data)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = TaskService(session)
    try:
        return await service.update_task(task_id, data)
    except TaskServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{task_id}/approve", response_model=TaskResponse)
async def approve_task(
    task_id: uuid.UUID,
    data: TaskApproveRequest,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = TaskService(session)
    try:
        return await service.approve_task(task_id, data.admin_notes)
    except TaskServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{task_id}/discard", response_model=TaskResponse)
async def discard_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = TaskService(session)
    try:
        return await service.discard_task(task_id)
    except TaskServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: uuid.UUID,
    admin_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = TaskService(session)
    try:
        return await service.assign_task(task_id, admin_id)
    except TaskServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
