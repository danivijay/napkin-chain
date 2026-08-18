"""Google OpenID Connect sign-in and user identity.

We run the authorization-code flow server-side: the browser never handles a
Google token, and the only thing that reaches it afterwards is our own
HttpOnly session cookie. Google's access token is discarded once the identity
is verified - nothing in the product needs it.
"""

import asyncio
from urllib.parse import urlencode

import httpx
import jwt
from bson import ObjectId
from bson.errors import InvalidId
from jwt import PyJWKClient

from app.core.config import settings
from app.core.logging import get_logger
from app.db.mongodb import Collections, collection
from app.models.common import utcnow
from app.models.user import GoogleIdentity, User

logger = get_logger(__name__)

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")

_jwk_client = PyJWKClient(GOOGLE_JWKS_URI, cache_keys=True)


class AuthError(Exception):
    """Sign-in failed. The message is for logs, never for the browser."""


def build_authorization_url(state: str) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"


async def exchange_code_for_identity(code: str) -> GoogleIdentity:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
    if response.status_code != httpx.codes.OK:
        raise AuthError(f"token exchange failed: {response.status_code} {response.text}")

    id_token = response.json().get("id_token")
    if not id_token:
        raise AuthError("token response contained no id_token")
    return await verify_id_token(id_token)


async def verify_id_token(id_token: str) -> GoogleIdentity:
    """Validate signature, audience and issuer against Google's JWKS."""

    def _verify() -> dict:
        signing_key = _jwk_client.get_signing_key_from_jwt(id_token)
        return jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.google_client_id,
            issuer=list(GOOGLE_ISSUERS),
            options={"require": ["exp", "iat", "sub", "aud", "iss"]},
        )

    try:
        claims = await asyncio.to_thread(_verify)
    except Exception as exc:  # noqa: BLE001 - any failure is a failed sign-in
        raise AuthError(f"id_token verification failed: {exc}") from exc

    if not claims.get("email"):
        raise AuthError("id_token has no email claim")
    if claims.get("email_verified") is False:
        raise AuthError("google account email is not verified")

    return GoogleIdentity(
        sub=claims["sub"],
        email=claims["email"],
        name=claims.get("name"),
        picture=claims.get("picture"),
    )


async def get_or_create_user(identity: GoogleIdentity) -> tuple[User, bool]:
    """Returns ``(user, created)``. Google's ``sub`` is the external identity key."""
    users = collection(Collections.users)
    now = utcnow()

    existing = await users.find_one_and_update(
        {"googleSub": identity.sub},
        {
            "$set": {
                "lastLoginAt": now,
                "email": identity.email,
                "name": identity.name,
                "avatarUrl": identity.picture,
            }
        },
        return_document=True,
    )
    if existing:
        return User.model_validate(existing), False

    document = {
        "schemaVersion": 1,
        "googleSub": identity.sub,
        "email": identity.email,
        "name": identity.name,
        "avatarUrl": identity.picture,
        "createdAt": now,
        "lastLoginAt": now,
        "preferences": {},
    }
    result = await users.insert_one(document)
    document["_id"] = result.inserted_id
    logger.info("auth.user_created", extra={"userId": str(result.inserted_id)})
    return User.model_validate(document), True


async def get_user_by_id(user_id: str) -> User | None:
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None
    doc = await collection(Collections.users).find_one({"_id": oid})
    return User.model_validate(doc) if doc else None


async def update_preferences(user_id: str, preferences: dict) -> User | None:
    doc = await collection(Collections.users).find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {f"preferences.{k}": v for k, v in preferences.items()}},
        return_document=True,
    )
    return User.model_validate(doc) if doc else None
