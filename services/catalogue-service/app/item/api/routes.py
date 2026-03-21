from fastapi import APIRouter, Depends, status

from app.item.application.dtos import (
    ItemResponse,
    UpdateItemRequest,
)
from app.item.application.service import ItemService
from app.dependencies import get_item_service

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    service: ItemService = Depends(get_item_service),
):
    item = service.get_item(item_id)
    entity_dict = item.from_entity()
    entity_dict["id"] = entity_dict.pop("_id", item.id)
    return ItemResponse(**entity_dict)


@router.patch("/{item_id}", status_code=status.HTTP_200_OK)
async def update_item(
    item_id: str,
    body: UpdateItemRequest,
    service: ItemService = Depends(get_item_service),
):
    update_data = body.model_dump(exclude_unset=True)
    service.update_item(item_id, update_data)
    return {"success": True}


@router.put("/{item_id}/custom-price/{business_id}", status_code=status.HTTP_200_OK)
async def set_custom_price(
    item_id: str,
    business_id: str,
    price: float,
    service: ItemService = Depends(get_item_service),
):
    service.set_custom_price(item_id, business_id, price)
    return {"success": True}


@router.delete("/{item_id}/custom-price/{business_id}", status_code=status.HTTP_200_OK)
async def remove_custom_price(
    item_id: str,
    business_id: str,
    service: ItemService = Depends(get_item_service),
):
    service.remove_custom_price(item_id, business_id)
    return {"success": True}
