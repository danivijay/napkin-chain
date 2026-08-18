"""Session cookies, CSRF tokens and rate limiting.

The application session is a short-lived signed JWT in an HttpOnly cookie.
We deliberately do not persist Google's OAuth access token: the only thing we
need from Google is a verified identity at login time.
"""

import hmac
import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Request, Response

from app.core.config import settings

SESSION_COOKIE = "nc_session"
CSRF_COOKIE = "nc_csrf"
CSRF_HEADER = "X-CSRF-Token"
OAUTH_STATE_COOKIE = "nc_oauth_state"

_ALGORITHM = "HS256"


class SessionError(Exception):
    """Raised when a session cookie is missing, malformed or expired."""


@dataclass(frozen=True)
class SessionClaims:
    user_id: str
    google_sub: str
    issued_at: datetime
    expires_at: datetime


def create_session_token(user_id: str, google_sub: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "gsub": google_sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings.session_ttl_seconds)).timestamp()),
    }
    return jwt.encode(payload, settings.session_secret, algorithm=_ALGORITHM)


def read_session_token(token: str) -> SessionClaims:
    try:
        payload = jwt.decode(token, settings.session_secret, algorithms=[_ALGORITHM])
    except jwt.PyJWTError as exc:  # expired, bad signature, malformed
        raise SessionError(str(exc)) from exc

    try:
        return SessionClaims(
            user_id=payload["sub"],
            google_sub=payload["gsub"],
            issued_at=datetime.fromtimestamp(payload["iat"], UTC),
            expires_at=datetime.fromtimestamp(payload["exp"], UTC),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SessionError("malformed session payload") from exc


def issue_session(response: Response, user_id: str, google_sub: str) -> None:
    """Set the session cookie plus a readable CSRF token (double-submit)."""
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(user_id, google_sub),
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )
    response.set_cookie(
        CSRF_COOKIE,
        secrets.token_urlsafe(32),
        max_age=settings.session_ttl_seconds,
        httponly=False,  # the SPA must read this to echo it back
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )


def clear_session(response: Response) -> None:
    for name in (SESSION_COOKIE, CSRF_COOKIE):
        response.delete_cookie(
            name,
            path="/",
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
        )


def csrf_token_valid(request: Request) -> bool:
    cookie = request.cookies.get(CSRF_COOKIE)
    header = request.headers.get(CSRF_HEADER)
    if not cookie or not header:
        return False
    return hmac.compare_digest(cookie, header)


def new_oauth_state() -> str:
    return secrets.token_urlsafe(24)


def set_oauth_state(response: Response, state: str) -> None:
    response.set_cookie(
        OAUTH_STATE_COOKIE,
        state,
        max_age=600,
        httponly=True,
        secure=settings.cookie_secure,
        # The callback is a top-level redirect from Google, so Lax is enough
        # and keeps the state cookie from being sent on unrelated cross-site
        # subrequests.
        samesite="lax",
        path="/",
    )


def oauth_state_valid(request: Request, state: str | None) -> bool:
    expected = request.cookies.get(OAUTH_STATE_COOKIE)
    if not expected or not state:
        return False
    return hmac.compare_digest(expected, state)


class RateLimiter:
    """In-process sliding-window limiter.

    Good enough for a single-instance MVP; swap for a shared store the moment
    the API runs on more than one worker.
    """

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        bucket = self._hits[key]
        cutoff = now - self.window
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True

    def reset(self) -> None:
        self._hits.clear()


auth_rate_limiter = RateLimiter(
    settings.auth_rate_limit, settings.auth_rate_window_seconds
)
submit_rate_limiter = RateLimiter(
    settings.submit_rate_limit, settings.submit_rate_window_seconds
)


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
