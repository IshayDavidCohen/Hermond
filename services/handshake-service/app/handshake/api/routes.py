from typing import List

from fastapi import APIRouter, Depends, status

from app.handshake.domain.entities.handshake import HandshakeStatus
from app.handshake.application.dtos import (
    CreateHandshakeRequest, CreateHandshakeResponse, HandshakeResponse,
)
from app.handshake.application.service import HandshakeService
from app.dependencies import get_handshake_service
from app.shared.exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/handshake", tags=["Handshake"])


def _handshake_to_response(h) -> HandshakeResponse:
    return HandshakeResponse(
        id=h.id, sender_id=h.sender_id, recipient_id=h.recipient_id,
        sender_type=h.sender_type, recipient_type=h.recipient_type,
        status=h.status.value, created_at=h.created_at, updated_at=h.updated_at,
    )


@router.post("/create", response_model=CreateHandshakeResponse, status_code=status.HTTP_201_CREATED)
async def create_handshake(body: CreateHandshakeRequest,
                           service: HandshakeService = Depends(get_handshake_service)):
    hid, created = service.create_handshake(
        sender_id=body.sender_id, recipient_id=body.recipient_id,
        sender_type=body.sender_type, recipient_type=body.recipient_type,
    )
    return CreateHandshakeResponse(id=hid, created=created, existed=not created)


@router.get("/get/{handshake_id}", response_model=HandshakeResponse)
async def get_handshake(handshake_id: str,
                        service: HandshakeService = Depends(get_handshake_service)):
    handshake = service.get_handshake(handshake_id)
    if not handshake:
        raise NotFoundError("Handshake not found")
    return _handshake_to_response(handshake)


@router.get("/get/user_handshakes/{user_type}/{user_id}", response_model=List[HandshakeResponse])
async def get_user_handshakes(user_type: str, user_id: str,
                              service: HandshakeService = Depends(get_handshake_service)):
    handshakes = service.list_user_handshakes(user_id=user_id, user_type=user_type)
    return [_handshake_to_response(h) for h in handshakes]


@router.post("/respond/{user_id}/{handshake_id}/{response}")
async def respond_handshake(user_id: str, handshake_id: str, response: str,
                            service: HandshakeService = Depends(get_handshake_service)):
    try:
        new_status = HandshakeStatus(response)
    except ValueError:
        raise ValidationError(f"Invalid response: {response}")
    ok = service.respond_to_handshake(actor_user_id=user_id, handshake_id=handshake_id, new_status=new_status)
    return {"success": ok}


@router.get("/ack/{user_id}/{handshake_id}/{response}")
async def ack_handshake(user_id: str, handshake_id: str, response: str,
                        service: HandshakeService = Depends(get_handshake_service)):
    try:
        new_status = HandshakeStatus(response)
    except ValueError:
        raise ValidationError(f"Invalid response: {response}")
    ok = service.respond_to_handshake(actor_user_id=user_id, handshake_id=handshake_id, new_status=new_status)
    return {"success": ok}


@router.delete("/close/{handshake_id}")
async def close_handshake(handshake_id: str,
                          service: HandshakeService = Depends(get_handshake_service)):
    ok = service.close_handshake(handshake_id)
    if not ok:
        raise NotFoundError("Handshake not found")
    return {"success": True}
