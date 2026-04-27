from pydantic import BaseModel
from datetime import datetime


class CreateHandshakeRequest(BaseModel):
    sender_id: str
    recipient_id: str
    sender_type: str
    recipient_type: str


class HandshakeResponse(BaseModel):
    id: str
    sender_id: str
    recipient_id: str
    sender_type: str
    recipient_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class CreateHandshakeResponse(BaseModel):
    id: str
    created: bool
    existed: bool
