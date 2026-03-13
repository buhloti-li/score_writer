from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_admin_user
from app.models.user import User
from app.schemas.order import OrderListResponse
from app.services.order_service import OrderService
from app.services.score_service import ScoreService
from app.services.task_service import TaskService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def dashboard(
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    score_service = ScoreService(session)
    task_service = TaskService(session)
    order_service = OrderService(session)

    scores, total_scores = await score_service.list_scores(0, 1)
    customer_tasks, customer_total = await task_service.list_by_type(
        "customer_transcribe", 0, 1
    )
    import_tasks, import_total = await task_service.list_by_type(
        "proactive_import", 0, 1
    )
    transcribe_tasks, transcribe_total = await task_service.list_by_type(
        "proactive_transcribe", 0, 1
    )

    pending_tasks = await task_service.list_customer_tasks(0, 100)
    pending_count = sum(
        1 for t in pending_tasks if t.status in ("pending", "processing", "review")
    )

    return {
        "total_scores": total_scores,
        "total_customer_tasks": customer_total,
        "total_import_tasks": import_total,
        "total_transcribe_tasks": transcribe_total,
        "pending_tasks": pending_count,
        "is_queue_idle": await task_service.is_queue_idle(),
    }


@router.get("/orders", response_model=OrderListResponse)
async def admin_list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = OrderService(session)
    offset = (page - 1) * page_size
    orders = await service.list_all_orders(offset, page_size)
    return OrderListResponse(
        items=orders, total=len(orders), page=page, page_size=page_size
    )
