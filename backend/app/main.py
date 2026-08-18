from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import attempts, auth, challenges, learning, progress, users
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.security import CSRF_HEADER
from app.db import mongodb
from app.db.indexes import ensure_indexes

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect()
    try:
        await ensure_indexes()
    except Exception as exc:  # noqa: BLE001 - the API can still serve reads
        logger.error("startup.index_failure", extra={"error": str(exc)})
    yield
    await mongodb.disconnect()


app = FastAPI(
    title="Napkin Chain API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", CSRF_HEADER],
)

for router in (
    auth.router,
    users.router,
    challenges.router,
    attempts.router,
    learning.router,
    progress.router,
):
    app.include_router(router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Client errors pass through; server errors never leak internals."""
    if exc.status_code >= 500:
        logger.error(
            "http.server_error",
            extra={"path": request.url.path, "status": exc.status_code},
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": "Server error"})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "That input doesn't look right."},
    )


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    logger.exception("http.unhandled", extra={"path": request.url.path})
    return JSONResponse(status_code=500, content={"detail": "Something went wrong."})


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db", tags=["health"])
async def health_db() -> dict[str, str]:
    """Reported separately so a cold database never fails the liveness probe."""
    return await mongodb.ping()
