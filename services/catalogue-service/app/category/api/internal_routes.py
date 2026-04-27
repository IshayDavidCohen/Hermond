from fastapi import APIRouter, Depends

from app.category.infrastructure.repository import CategoryRepository
from app.dependencies import get_category_repo

router = APIRouter(tags=["Internal - Categories"])


@router.get("/internal/categories/{category_id}/users")
async def get_category_users(
    category_id: str,
    repo: CategoryRepository = Depends(get_category_repo),
):
    users = repo.get_users(category_id)
    return {"users": users}


@router.post("/internal/categories/{category_id}/add-user")
async def add_user_to_category(
    category_id: str,
    username: str,
    supplier_id: str,
    repo: CategoryRepository = Depends(get_category_repo),
):
    ok = repo.add_user_to_category(category_id, username, supplier_id)
    return {"success": ok}


@router.post("/internal/categories/{category_id}/remove-user")
async def remove_user_from_category(
    category_id: str,
    username: str,
    repo: CategoryRepository = Depends(get_category_repo),
):
    ok = repo.remove_user_from_category(category_id, username)
    return {"success": ok}
