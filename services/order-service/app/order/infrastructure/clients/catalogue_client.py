import logging
from typing import Dict, List

import httpx

logger = logging.getLogger(__name__)


class CatalogueClient:
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    async def get_items_batch(self, item_ids: List[str]) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self._base_url}/internal/items/batch", json=item_ids)
            resp.raise_for_status()
            return resp.json()
