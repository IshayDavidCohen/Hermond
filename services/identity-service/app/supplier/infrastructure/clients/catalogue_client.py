import logging
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class CatalogueClient:
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    async def create_item(self, item_data: Dict) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self._base_url}/api/v1/items", json=item_data)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json().get("id")

    async def item_exists(self, item_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/internal/items/{item_id}/exists")
            resp.raise_for_status()
            return resp.json().get("exists", False)

    async def get_items_batch(self, item_ids: List[str]) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self._base_url}/internal/items/batch", json=item_ids)
            resp.raise_for_status()
            return resp.json()

    async def get_supplier_id_from_item(self, item_id: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/api/v1/items/{item_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json().get("supplier_id")

    async def delete_item(self, item_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{self._base_url}/api/v1/items/{item_id}")
            return resp.status_code < 400

    async def get_category_users(self, category_id: str) -> Dict[str, str]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/internal/categories/{category_id}/users")
            resp.raise_for_status()
            return resp.json().get("users", {})

    async def add_user_to_category(self, category_id: str, username: str, supplier_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/internal/categories/{category_id}/add-user",
                params={"username": username, "supplier_id": supplier_id},
            )
            resp.raise_for_status()
            return resp.json().get("success", False)

    async def remove_user_from_category(self, category_id: str, username: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/internal/categories/{category_id}/remove-user",
                params={"username": username},
            )
            resp.raise_for_status()
            return resp.json().get("success", False)

    async def get_items_by_supplier(self, supplier_id: str) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/internal/items/batch",
                json=[],
                params={"supplier_id": supplier_id},
            )
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            return resp.json()
