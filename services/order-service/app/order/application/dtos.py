from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class OrderedItemSchema(BaseModel):
    item_id: str
    quantity: int
    base_price: float
    price_at_order: float
    total_price_for_item: float


class CreateOrderRequest(BaseModel):
    business: str
    orders: Dict[str, Dict[str, int]]


class OrderResponse(BaseModel):
    id: str
    supplier_id: str
    business_id: str
    estimated_eta: Optional[datetime] = None
    ordered_items: List[OrderedItemSchema]
    total_price: float
    status: str
    created_at: datetime
    updated_at: datetime


class UpdateOrderStatusRequest(BaseModel):
    status: str


class PaginatedOrdersResponse(BaseModel):
    items: List[OrderResponse]
    next_cursor: Optional[str] = None # ISO timestamp of the last item's updated_at or None when exhausted
    has_more: bool
    total: Optional[int] = None
