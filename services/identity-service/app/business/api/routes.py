from fastapi import APIRouter, Depends, status

from app.business.application.dtos import (
    CreateBusinessRequest,
    CreateBusinessResponse,
    BusinessResponse,
    UpdateBusinessRequest,
)
from app.business.application.service import BusinessService
from app.dependencies import get_business_service

router = APIRouter(prefix="/business", tags=["Business"])


@router.post(
    "/create/profile",
    response_model=CreateBusinessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_business(
    body: CreateBusinessRequest,
    service: BusinessService = Depends(get_business_service),
):
    business_id = service.create_business(body.model_dump())
    return CreateBusinessResponse(id=business_id)


@router.get("/get/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: str,
    service: BusinessService = Depends(get_business_service),
):
    business = service.get_business(business_id)
    entity_dict = business.from_entity()
    entity_dict["id"] = entity_dict.pop("_id", business.id)
    return BusinessResponse(**entity_dict)


@router.patch("/update/{business_id}", status_code=status.HTTP_200_OK)
async def update_business(
    business_id: str,
    body: UpdateBusinessRequest,
    service: BusinessService = Depends(get_business_service),
):
    update_data = body.model_dump(exclude_unset=True)
    service.update_business(business_id, update_data)
    return {"success": True}


@router.delete("/delete/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: str,
    service: BusinessService = Depends(get_business_service),
):
    service.delete_business(business_id)
