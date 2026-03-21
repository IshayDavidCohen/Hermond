from pydantic import BaseModel
from typing import Dict
from datetime import datetime


class CreateCategoryRequest(BaseModel):
    oid: str
    title: str
    icon: str
    image: str
    users: Dict[str, str] = {}


class CategoryResponse(BaseModel):
    oid: str
    title: str
    icon: str
    image: str
    users: Dict[str, str]
    created_at: datetime
    updated_at: datetime


class CreateCategoryResponse(BaseModel):
    id: str
