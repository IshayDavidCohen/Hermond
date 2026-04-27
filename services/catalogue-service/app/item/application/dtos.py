from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

class UnitType(str, Enum):
    # Weight
    KG = "kg"
    G = "g"
    LB = "lb"
    OZ = "oz"
    # Volume
    LITRE = "litre"
    ML = "ml"
    GALLON = "gallon"
    QUART = "quart"
    PINT = "pint"
    FL_OZ = "fl-oz"
    # Packaging
    UNIT = "unit"
    EACH = "each"
    PIECE = "piece"
    BOTTLE = "bottle"
    BOX = "box"
    BUNDLE = "bundle"
    CASE = "case"
    DOZEN = "dozen"
    KEG = "keg"
    LOAF = "loaf"
    RACK = "rack"
    FOUR_PACK = "4-pack"
    SIX_PACK = "6-pack"

class StockStatus(str, Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    LOW_STOCK = "low_stock"

class CreateItemRequest(BaseModel):
    supplier_id: str
    name: str
    category: str
    image: str
    desc: str
    base_price: float
    unit: UnitType
    currency: str
    stock_quantity: int = 0
    out_of_stock: bool = False


class UpdateItemRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    desc: Optional[str] = None
    base_price: Optional[float] = None
    unit: Optional[UnitType] = None
    currency: Optional[str] = None
    stock_quantity: Optional[int] = None
    out_of_stock: Optional[bool] = None


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
    stock_quantity: int
    out_of_stock: bool
    created_at: datetime
    updated_at: datetime


class CreateItemResponse(BaseModel):
    id: str