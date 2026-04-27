from typing import List, Dict

from fastapi import APIRouter, Depends, status

from app.supplier.application.dtos import (
    CreateSupplierRequest,
    CreateSupplierResponse,
    SupplierResponse,
    UpdateSupplierRequest,
)
from app.supplier.application.service import SupplierService
from app.item.application.dtos import CreateItemRequest
from app.dependencies import get_supplier_service

router = APIRouter(prefix="/supplier", tags=["Supplier"])


def _supplier_to_carousel_item(supplier) -> Dict:
    return {
        "link": supplier.id,
        "title": supplier.company_name,
        "desc": supplier.desc,
        "banner": supplier.banner,
        "icon": supplier.icon,
    }


@router.post(
    "/create/profile",
    response_model=CreateSupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplier(
    body: CreateSupplierRequest,
    service: SupplierService = Depends(get_supplier_service),
):
    supplier_id, category_map = await service.create_supplier(body.model_dump())
    return CreateSupplierResponse(id=supplier_id, category_validity_map=category_map)


@router.get("/get/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    service: SupplierService = Depends(get_supplier_service),
):
    supplier = service.get_supplier(supplier_id)
    entity_dict = supplier.from_entity()
    entity_dict["id"] = entity_dict.pop("_id", supplier.id)
    entity_dict["business_id"] = entity_dict.pop("bid", supplier.business_id)
    return SupplierResponse(**entity_dict)


@router.get("/get/category_carousel/{category_id}")
async def get_category_carousel(
    category_id: str,
    service: SupplierService = Depends(get_supplier_service),
):
    suppliers = await service.get_suppliers_from_category(category_id)
    data_list = [_supplier_to_carousel_item(s) for s in suppliers]
    keys = {
        "link": "link",
        "title": "title",
        "desc": "desc",
        "banner": "banner",
        "icon": "icon",
    }
    carousel = [{k: element[v] for k, v in keys.items()} for element in data_list]
    return carousel


@router.post("/create/item", status_code=status.HTTP_201_CREATED)
async def create_supplier_item(
    body: CreateItemRequest,
    service: SupplierService = Depends(get_supplier_service),
):
    item_id = await service.create_item(body.model_dump())
    return {"id": item_id}


@router.delete("/delete/item/{item_id}")
async def delete_supplier_item(
    item_id: str,
    service: SupplierService = Depends(get_supplier_service),
):
    await service.delete_item(item_id)
    return {"success": True}


@router.get("/get/{supplier_id}/items")
async def get_supplier_items(
    supplier_id: str,
    business_id: str = None,
    service: SupplierService = Depends(get_supplier_service),
):
    items = await service.get_supplier_items(supplier_id, business_id)
    return items


@router.patch("/update/{supplier_id}", status_code=status.HTTP_200_OK)
async def update_supplier(
    supplier_id: str,
    body: UpdateSupplierRequest,
    service: SupplierService = Depends(get_supplier_service),
):
    update_data = body.model_dump(exclude_unset=True)
    service.update_supplier(supplier_id, update_data)
    return {"success": True}


@router.delete("/delete/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: str,
    service: SupplierService = Depends(get_supplier_service),
):
    service.delete_supplier(supplier_id)
