import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.shared.exceptions import VendorError

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        logger.info("[%s] %s %s", request_id, request.method, request.url.path)
        response = await call_next(request)
        logger.info("[%s] completed %d", request_id, response.status_code)
        return response

    @app.exception_handler(VendorError)
    async def vendor_error_handler(_request: Request, exc: VendorError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": type(exc).__name__, "detail": exc.detail},
        )
