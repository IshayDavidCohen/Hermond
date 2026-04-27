from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.order.application.dtos import (
    CreateOrderRequest,
    OrderResponse,
    OrderedItemSchema,
    UpdateOrderStatusRequest,
    PaginatedOrdersResponse
)
from app.order.application.service import OrderService
from app.dependencies import get_order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


def _order_to_response(order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        supplier_id=order.supplier_id,
        business_id=order.business_id,
        estimated_eta=order.estimated_eta,
        ordered_items=[
            OrderedItemSchema(
                item_id=oi.item_id,
                quantity=oi.quantity,
                base_price=oi.base_price,
                price_at_order=oi.price_at_order,
                total_price_for_item=oi.total_price_for_item,
            )
            for oi in order.ordered_items
        ],
        total_price=order.total_price,
        status=order.status.value,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_order(
    body: CreateOrderRequest,
    service: OrderService = Depends(get_order_service),
):
    result = await service.create_order_for_each_supplier(body.model_dump())
    return result


@router.get("/active/{order_id}", response_model=OrderResponse)
async def get_active_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    order = service.get_active_order(order_id)
    return _order_to_response(order)


@router.get("/history/{order_id}", response_model=OrderResponse)
async def get_order_history(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    order = service.get_order_from_history(order_id)
    return _order_to_response(order)


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: str,
    body: UpdateOrderStatusRequest,
    service: OrderService = Depends(get_order_service),
):
    service.update_order_status(order_id, body.status)
    return {"success": True}


@router.get("/business/{biz_id}", response_model=List[OrderResponse])
async def list_business_orders(
    biz_id: str,
    since: Optional[datetime] = Query(default=None),
    service: OrderService = Depends(get_order_service),
):
    orders = service.list_business_orders(biz_id, since=since)
    return [_order_to_response(o) for o in orders]

@router.get("/supplier/{sup_id}", response_model=List[OrderResponse])
async def list_supplier_orders(
    sup_id: str,
    since: Optional[datetime] = Query(default=None),
    service: OrderService = Depends(get_order_service),
):
    orders = service.list_supplier_orders(sup_id, since=since)
    return [_order_to_response(o) for o in orders]


@router.post("/{order_id}/archive", status_code=status.HTTP_200_OK)
async def archive_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    service.archive_order(order_id)
    return {"success": True}

@router.get("/business/{biz_id}/history", response_model=PaginatedOrdersResponse)
async def list_business_history(
    biz_id: str,
    cursor: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    service: OrderService = Depends(get_order_service),
):

    orders, next_cursor, has_more, total = service.list_business_history(biz_id, cursor=cursor, limit=limit)

    return PaginatedOrdersResponse(
        items=[_order_to_response(o) for o in orders],
        next_cursor=next_cursor,
        has_more=has_more,
        total=total if total >= 0 else None
    )

@router.get("/supplier/{sup_id}/history", response_model=PaginatedOrdersResponse)
async def list_supplier_history(
    sup_id: str,
    cursor: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    service: OrderService = Depends(get_order_service),
):
    orders, next_cursor, has_more, total = service.list_supplier_history(sup_id, cursor=cursor, limit=limit)
    return PaginatedOrdersResponse(
        items=[_order_to_response(o) for o in orders],
        next_cursor=next_cursor,
        has_more=has_more,
        total=total if total >= 0 else None
    )

# Run against the vendor_order database, either via mongosh or a migration script:
# db.order_history.createIndex({ business_id: 1, updated_at: -1 })
# db.order_history.createIndex({ supplier_id: 1, updated_at: -1 })
# db.active_orders.createIndex({ business_id: 1 })
# db.active_orders.createIndex({ supplier_id: 1 })
# Without these, the get_order_history_page query does a collection scan. With them, cursor pagination is O(log N) per page.
