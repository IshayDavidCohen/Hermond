from fastapi import APIRouter, Depends

from app.business.infrastructure.repository import BusinessRepository
from app.dependencies import get_business_repo

router = APIRouter(tags=["Internal - Business"])


@router.get("/internal/business/{business_id}/exists")
async def business_exists(
    business_id: str,
    repo: BusinessRepository = Depends(get_business_repo),
):
    return {"exists": repo.exists(business_id)}


@router.post("/internal/business/{business_id}/add-active-order")
async def add_active_order(
    business_id: str,
    order_id: str,
    repo: BusinessRepository = Depends(get_business_repo),
):
    ok = repo.add_active_order(business_id, order_id)
    return {"success": ok}
