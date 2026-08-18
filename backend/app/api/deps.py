"""Request-scoped dependencies: identity, CSRF, rate limiting."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.core.security import (
    SESSION_COOKIE,
    SessionError,
    auth_rate_limiter,
    client_key,
    csrf_token_valid,
    read_session_token,
    submit_rate_limiter,
)
from app.models.user import User
from app.services import auth_service

UNAUTHENTICATED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
)


async def get_current_user(request: Request) -> User:
    """The only source of user identity. A userId from the client is ignored."""
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise UNAUTHENTICATED
    try:
        claims = read_session_token(token)
    except SessionError as exc:
        raise UNAUTHENTICATED from exc

    user = await auth_service.get_user_by_id(claims.user_id)
    if user is None or user.google_sub != claims.google_sub:
        raise UNAUTHENTICATED
    return user


async def get_optional_user(request: Request) -> User | None:
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


def require_csrf(request: Request) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    if not csrf_token_valid(request):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token"
        )


def auth_rate_limit(request: Request) -> None:
    if not auth_rate_limiter.allow(f"auth:{client_key(request)}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Try again shortly.",
        )


def submit_rate_limit(request: Request) -> None:
    if not submit_rate_limiter.allow(f"submit:{client_key(request)}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Slow down a moment.",
        )


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
CsrfProtected = Annotated[None, Depends(require_csrf)]
