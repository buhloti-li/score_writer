import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_admin_user, get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderListResponse, OrderResponse, PaymentCallback
from app.services.order_service import OrderService, OrderServiceError

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = OrderService(session)
    try:
        order = await service.create_order(
            user_id=user.id,
            score_id=data.score_id,
            task_id=data.task_id,
            amount=data.amount,
            source=data.source.value,
            payment_method=data.payment_method,
        )
        return order
    except OrderServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=OrderListResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = OrderService(session)
    offset = (page - 1) * page_size
    orders = await service.get_user_orders(user.id, offset, page_size)
    return OrderListResponse(items=orders, total=len(orders), page=page, page_size=page_size)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = OrderService(session)
    try:
        order = await service.get_order(order_id)
        if order.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")
        return order
    except OrderServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{order_id}/pay", response_model=OrderResponse)
async def mark_order_paid(
    order_id: uuid.UUID,
    callback: PaymentCallback,
    session: AsyncSession = Depends(get_db),
):
    service = OrderService(session)
    try:
        return await service.mark_paid(order_id, callback.payment_method)
    except OrderServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/deliver", response_model=OrderResponse)
async def deliver_order(
    order_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = OrderService(session)
    try:
        return await service.mark_delivered(order_id)
    except OrderServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/refund", response_model=OrderResponse)
async def refund_order(
    order_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    service = OrderService(session)
    try:
        return await service.refund(order_id)
    except OrderServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
