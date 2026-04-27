from fastapi import APIRouter, Depends

from app.supplier.infrastructure.repository import SupplierRepository
from app.dependencies import get_supplier_repo

router = APIRouter(tags=["Internal - Supplier"])


@router.get("/internal/supplier/{supplier_id}/exists")
async def supplier_exists(
    supplier_id: str,
    repo: SupplierRepository = Depends(get_supplier_repo),
):
    return {"exists": repo.exists(supplier_id)}


@router.post("/internal/supplier/{supplier_id}/add-active-order")
async def add_active_order(
    supplier_id: str,
    order_id: str,
    repo: SupplierRepository = Depends(get_supplier_repo),
):
    ok = repo.add_active_order(supplier_id, order_id)
    return {"success": ok}


@router.get("/internal/supplier/{supplier_id}/summary")
async def supplier_summary(
    supplier_id: str,
    repo: SupplierRepository = Depends(get_supplier_repo),
):
    supplier = repo.get_supplier(supplier_id)
    if not supplier:
        return {"exists": False}
    return {
        "exists": True,
        "id": supplier.id,
        "company_name": supplier.company_name,
        "categories": supplier.categories,
    }
