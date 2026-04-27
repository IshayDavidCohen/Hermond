from typing import List

from fastapi import APIRouter, Depends

from app.item.infrastructure.repository import ItemRepository
from app.dependencies import get_item_repo
from app.shared.utils import to_oid

router = APIRouter(tags=["Internal - Items"])


@router.post("/internal/items/batch")
async def get_items_batch(
    item_ids: List[str],
    repo: ItemRepository = Depends(get_item_repo),
):
    oids = [to_oid(i) for i in item_ids]
    oids = [o for o in oids if o is not None]
    if not oids:
        return []
    cursor = repo.get_items_by(query={"_id": {"$in": oids}})
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if "supplier_id" in doc:
            doc["supplier_id"] = str(doc["supplier_id"])
        results.append(doc)
    return results


@router.get("/internal/items/{item_id}/exists")
async def item_exists(
    item_id: str,
    repo: ItemRepository = Depends(get_item_repo),
):
    return {"exists": repo.item_exists(item_id)}
