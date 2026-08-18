from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, CsrfProtected
from app.schemas.auth import UserOut
from app.services import progress_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        preferences=user.preferences.model_dump(by_alias=True),
    )


@router.delete("/me/progress", status_code=status.HTTP_204_NO_CONTENT)
async def reset_progress(user: CurrentUser, _: CsrfProtected = None) -> Response:
    """Wipes attempts and mastery for this user only. Challenges are untouched."""
    await progress_service.delete_user_progress(user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
