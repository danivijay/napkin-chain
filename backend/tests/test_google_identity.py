"""Verification of Google's id_tokens.

This suite exists because the local dev sign-in bypasses Google entirely, so
nothing else exercises this path. A missing RS256 backend once made every real
sign-in fail while every test and every local login passed.
"""

import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import settings
from app.services import auth_service
from app.services.auth_service import AuthError, verify_id_token

KEY_ID = "test-key"


@pytest.fixture
def signing_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def google_keys(signing_key, monkeypatch):
    """Stand in for Google's JWKS with a key we control."""
    public_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(
        signing_key.public_key(), as_dict=True
    )
    public_jwk.update({"kid": KEY_ID, "use": "sig", "alg": "RS256"})
    key_set = jwt.PyJWKSet.from_dict({"keys": [public_jwk]})

    async def fake_keys():
        return key_set

    monkeypatch.setattr(auth_service, "_signing_keys", fake_keys)
    return key_set


@pytest.fixture(autouse=True)
def client_id(monkeypatch):
    monkeypatch.setattr(settings, "google_client_id", "test-client-id")


def encode(signing_key, **overrides) -> str:
    now = int(time.time())
    claims = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "sub": "1234567890",
        "email": "engineer@example.com",
        "email_verified": True,
        "name": "Test Engineer",
        "picture": "https://example.com/avatar.png",
        "iat": now,
        "exp": now + 3600,
        **overrides,
    }
    return jwt.encode(claims, signing_key, algorithm="RS256", headers={"kid": KEY_ID})


class TestValidToken:
    async def test_rs256_can_actually_be_verified(self, signing_key, google_keys):
        """Guards the dependency: PyJWT needs the crypto extra for RS256."""
        identity = await verify_id_token(encode(signing_key))
        assert identity.sub == "1234567890"
        assert identity.email == "engineer@example.com"

    async def test_only_the_claims_we_need_are_kept(self, signing_key, google_keys):
        identity = await verify_id_token(
            encode(signing_key, hd="example.com", locale="en", given_name="Test")
        )
        stored = identity.model_dump()
        assert set(stored) == {"sub", "email", "name", "picture"}


class TestRejection:
    async def test_a_token_for_another_client_is_rejected(self, signing_key, google_keys):
        with pytest.raises(AuthError):
            await verify_id_token(encode(signing_key, aud="someone-elses-client-id"))

    async def test_a_token_from_another_issuer_is_rejected(self, signing_key, google_keys):
        with pytest.raises(AuthError):
            await verify_id_token(encode(signing_key, iss="https://evil.example.com"))

    async def test_an_expired_token_is_rejected(self, signing_key, google_keys):
        now = int(time.time())
        with pytest.raises(AuthError):
            await verify_id_token(encode(signing_key, iat=now - 7200, exp=now - 3600))

    async def test_a_token_signed_by_an_unknown_key_is_rejected(self, google_keys):
        attacker = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with pytest.raises(AuthError):
            await verify_id_token(encode(attacker))

    async def test_an_unsigned_token_is_rejected(self, signing_key, google_keys):
        now = int(time.time())
        forged = jwt.encode(
            {
                "iss": "https://accounts.google.com",
                "aud": "test-client-id",
                "sub": "1",
                "email": "attacker@example.com",
                "iat": now,
                "exp": now + 3600,
            },
            key="",
            algorithm="none",
            headers={"kid": KEY_ID},
        )
        with pytest.raises(AuthError):
            await verify_id_token(forged)

    async def test_an_unverified_email_is_rejected(self, signing_key, google_keys):
        with pytest.raises(AuthError):
            await verify_id_token(encode(signing_key, email_verified=False))

    @pytest.mark.parametrize("garbage", ["", "not-a-jwt", "aaa.bbb.ccc"])
    async def test_malformed_tokens_are_rejected(self, garbage, google_keys):
        with pytest.raises(AuthError):
            await verify_id_token(garbage)
