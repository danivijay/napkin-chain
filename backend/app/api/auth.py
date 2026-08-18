from fastapi import APIRouter, Depends, Query, Request, Response, status
from pydantic import ValidationError
from fastapi.responses import RedirectResponse

from app.api.deps import CurrentUser, CsrfProtected, auth_rate_limit
from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import (
    OAUTH_STATE_COOKIE,
    clear_session,
    issue_session,
    new_oauth_state,
    oauth_state_valid,
    set_oauth_state,
)
from app.models.event import EventName
from app.models.user import GoogleIdentity, User
from app.schemas.auth import AuthStatus, DevLoginIn, UserOut
from app.services import analytics_service, auth_service
from app.services.auth_service import AuthError

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = get_logger(__name__)


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        preferences=user.preferences.model_dump(by_alias=True),
    )


async def _sign_in(response: Response, identity: GoogleIdentity) -> User:
    user, created = await auth_service.get_or_create_user(identity)
    issue_session(response, user.id, user.google_sub)
    await analytics_service.track(
        EventName.signup if created else EventName.login, user_id=user.id
    )
    return user


@router.get("/me", response_model=AuthStatus)
async def me(request: Request) -> AuthStatus:
    from app.api.deps import get_optional_user

    user = await get_optional_user(request)
    return AuthStatus(
        authenticated=user is not None,
        user=_user_out(user) if user else None,
        google_enabled=settings.google_configured,
        dev_login_enabled=settings.is_local,
    )


@router.get("/google/start", dependencies=[Depends(auth_rate_limit)])
async def google_start(redirect_to: str = Query(default="/app", alias="redirectTo")):
    if not settings.google_configured:
        return RedirectResponse(
            f"{settings.frontend_url}/login?error=google_not_configured"
        )

    state = new_oauth_state()
    response = RedirectResponse(auth_service.build_authorization_url(state))
    set_oauth_state(response, state)
    # Where to land inside the app afterwards; a path, never an absolute URL.
    safe_path = redirect_to if redirect_to.startswith("/") else "/app"
    response.set_cookie(
        "nc_post_login",
        safe_path,
        max_age=600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/google/callback", dependencies=[Depends(auth_rate_limit)])
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    landing = request.cookies.get("nc_post_login", "/app")
    failure = RedirectResponse(f"{settings.frontend_url}/login?error=auth_failed")

    if error or not code:
        logger.warning("auth.callback_error", extra={"error": error})
        return failure
    if not oauth_state_valid(request, state):
        logger.warning("auth.state_mismatch")
        return failure

    try:
        identity = await auth_service.exchange_code_for_identity(code)
    except AuthError as exc:
        logger.warning("auth.exchange_failed", extra={"error": str(exc)})
        return failure

    response = RedirectResponse(f"{settings.frontend_url}{landing}")
    await _sign_in(response, identity)
    response.delete_cookie(OAUTH_STATE_COOKIE, path="/")
    response.delete_cookie("nc_post_login", path="/")
    return response


@router.post("/dev-login", response_model=AuthStatus)
async def dev_login(payload: DevLoginIn, response: Response, request: Request):
    """Local-only sign-in so the product is runnable without Google credentials."""
    if not settings.is_local:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    auth_rate_limit(request)
    try:
        identity = GoogleIdentity(
            sub=f"dev|{payload.email}", email=payload.email, name=payload.name
        )
    except ValidationError as exc:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="That doesn't look like an email address.",
        ) from exc
    user = await _sign_in(response, identity)
    return AuthStatus(
        authenticated=True,
        user=_user_out(user),
        google_enabled=settings.google_configured,
        dev_login_enabled=True,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, request: Request) -> None:
    from app.api.deps import get_optional_user

    user = await get_optional_user(request)
    clear_session(response)
    if user:
        await analytics_service.track(EventName.logout, user_id=user.id)


@router.get("/session", response_model=UserOut)
async def session(user: CurrentUser) -> UserOut:
    return _user_out(user)


@router.post("/preferences", response_model=UserOut)
async def preferences(
    payload: dict, user: CurrentUser, _: CsrfProtected = None
) -> UserOut:
    allowed = {k: v for k, v in payload.items() if k in {"defaultMode", "reducedMotion"}}
    updated = await auth_service.update_preferences(user.id, allowed)
    return _user_out(updated or user)
