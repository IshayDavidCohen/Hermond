from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional
from datetime import datetime


class CreateBusinessRequest(BaseModel):
    bid: str
    company_name: str
    desc: str
    icon: str
    banner: str
    email: EmailStr
    phone: str
    address: str
    shipping_address: str
    categories: List[str]


class UpdateBusinessRequest(BaseModel):
    company_name: Optional[str] = None
    desc: Optional[str] = None
    icon: Optional[str] = None
    banner: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    shipping_address: Optional[str] = None
    categories: Optional[List[str]] = None


class BusinessResponse(BaseModel):
    id: str
    bid: str
    company_name: str
    desc: str
    icon: str
    banner: str
    email: str
    phone: str
    address: str
    shipping_address: str
    categories: List[str]
    my_suppliers: Dict[str, str]
    handshake_requests: Dict[str, str]
    active_orders: List[str]
    order_history: List[str]
    created_at: datetime
    updated_at: datetime


class CreateBusinessResponse(BaseModel):
    id: str
