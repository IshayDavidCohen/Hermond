from typing import List

from fastapi import APIRouter, Depends, status

from app.order.application.dtos import (
    CreateOrderRequest,
    OrderResponse,
    OrderedItemSchema,
    UpdateOrderStatusRequest,
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
    service: OrderService = Depends(get_order_service),
):
    orders = service.list_business_active_orders(biz_id)
    return [_order_to_response(o) for o in orders]


@router.get("/supplier/{sup_id}", response_model=List[OrderResponse])
async def list_supplier_orders(
    sup_id: str,
    service: OrderService = Depends(get_order_service),
):
    orders = service.list_supplier_active_orders(sup_id)
    return [_order_to_response(o) for o in orders]


@router.post("/{order_id}/archive", status_code=status.HTTP_200_OK)
async def archive_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    service.archive_order(order_id)
    return {"success": True}
