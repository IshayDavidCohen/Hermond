from typing import List

from fastapi import APIRouter, Depends, status

from app.category.application.dtos import (
    CreateCategoryRequest,
    CreateCategoryResponse,
    CategoryResponse,
)
from app.category.application.service import CategoryService
from app.dependencies import get_category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    service: CategoryService = Depends(get_category_service),
):
    categories = service.list_categories()
    return [
        CategoryResponse(
            oid=c.oid,
            title=c.title,
            icon=c.icon,
            image=c.image,
            users=c.users,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in categories
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service),
):
    c = service.get_category(category_id)
    return CategoryResponse(
        oid=c.oid,
        title=c.title,
        icon=c.icon,
        image=c.image,
        users=c.users,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.post("", response_model=CreateCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    body: CreateCategoryRequest,
    service: CategoryService = Depends(get_category_service),
):
    category_id = service.create_category(body.model_dump())
    return CreateCategoryResponse(id=category_id)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service),
):
    service.delete_category(category_id)
