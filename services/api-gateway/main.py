import logging

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Gateway", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROUTE_MAP = {
    "/api/v1/business": settings.IDENTITY_SERVICE_URL,
    "/api/v1/supplier": settings.IDENTITY_SERVICE_URL,
    "/api/v1/items": settings.CATALOGUE_SERVICE_URL,
    "/api/v1/categories": settings.CATALOGUE_SERVICE_URL,
    "/api/v1/handshake": settings.HANDSHAKE_SERVICE_URL,
    "/api/v1/orders": settings.ORDER_SERVICE_URL,
}


def _resolve_upstream(path: str) -> str | None:
    for prefix, url in ROUTE_MAP.items():
        if path.startswith(prefix):
            return url
    return None


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(path: str, request: Request):
    full_path = f"/{path}"
    upstream = _resolve_upstream(full_path)
    if not upstream:
        return Response(content='{"error": "no upstream for path"}', status_code=404, media_type="application/json")

    url = f"{upstream}{full_path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
                media_type=resp.headers.get("content-type"),
            )
        except httpx.RequestError as e:
            logger.error("Upstream error: %s", e)
            return Response(
                content=f'{{"error": "upstream unavailable", "detail": "{e}"}}',
                status_code=502,
                media_type="application/json",
            )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}
