import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class IdentityClient:
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    async def business_exists(self, business_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/internal/business/{business_id}/exists")
            resp.raise_for_status()
            return resp.json().get("exists", False)

    async def supplier_exists(self, supplier_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/internal/supplier/{supplier_id}/exists")
            resp.raise_for_status()
            return resp.json().get("exists", False)

    async def add_business_active_order(self, business_id: str, order_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/internal/business/{business_id}/add-active-order",
                params={"order_id": order_id},
            )
            resp.raise_for_status()
            return resp.json().get("success", False)

    async def add_supplier_active_order(self, supplier_id: str, order_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/internal/supplier/{supplier_id}/add-active-order",
                params={"order_id": order_id},
            )
            resp.raise_for_status()
            return resp.json().get("success", False)
