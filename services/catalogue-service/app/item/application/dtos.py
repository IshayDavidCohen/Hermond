from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime


class CreateItemRequest(BaseModel):
    supplier_id: str
    name: str
    category: str
    image: str
    desc: str
    base_price: float
    unit: str
    currency: str


class UpdateItemRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    desc: Optional[str] = None
    base_price: Optional[float] = None
    unit: Optional[str] = None
    currency: Optional[str] = None


class ItemResponse(BaseModel):
    id: str
    supplier_id: str
    name: str
    category: str
    image: str
    desc: str
    base_price: float
    unit: str
    currency: str
    custom_prices: Dict[str, float]
    created_at: datetime
    updated_at: datetime


class CreateItemResponse(BaseModel):
    id: str
