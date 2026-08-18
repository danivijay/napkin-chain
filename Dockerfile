# Multi-stage: build the SPA with Node, run it from Python.
#
# A container rather than Render's native Python runtime, for two reasons:
# the build needs both Node and Python and we should not depend on a host's
# build image happening to ship both, and this image runs unchanged on any
# container host if we ever move.

FROM node:22-slim AS frontend
WORKDIR /build

# Dependencies first, so a source-only change reuses the cached install layer.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.13-slim AS runtime
WORKDIR /srv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    SERVE_FRONTEND=true \
    FRONTEND_DIST=/srv/frontend/dist

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY --from=frontend /build/dist ./frontend/dist

# Run as a non-root user; nothing here needs to write to the filesystem.
RUN useradd --create-home --uid 10001 napkin && chown -R napkin:napkin /srv
USER napkin

WORKDIR /srv/backend

# Hosts inject the port they want; default to 8000 for a plain `docker run`.
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
