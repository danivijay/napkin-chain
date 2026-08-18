"""Serves the built React app alongside the API.

Deploying the frontend and API as one origin keeps the session cookie
first-party. It also means client-side routes like /app/challenges/x/build
have to fall through to index.html rather than 404.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Paths the SPA must never shadow.
API_PREFIXES = ("/api", "/health", "/docs", "/openapi.json")


def mount_frontend(app: FastAPI) -> bool:
    dist = Path(settings.frontend_dist)
    if not dist.is_absolute():
        dist = (Path(__file__).resolve().parents[2] / dist).resolve()

    index = dist / "index.html"
    if not index.is_file():
        logger.warning("spa.build_missing", extra={"path": str(dist)})
        return False

    # Hashed filenames, so the bundle can be cached hard; index.html cannot.
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(request: Request, full_path: str):
        if request.url.path.startswith(API_PREFIXES):
            return JSONResponse(status_code=404, content={"detail": "Not found"})

        candidate = (dist / full_path).resolve()
        # Only serve real files that are genuinely inside the build directory.
        if full_path and candidate.is_file() and candidate.is_relative_to(dist):
            return FileResponse(candidate)

        return FileResponse(index, headers={"Cache-Control": "no-cache"})

    logger.info("spa.mounted", extra={"path": str(dist)})
    return True
