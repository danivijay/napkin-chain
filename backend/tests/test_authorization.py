"""Nothing user-specific is reachable without a session, and never across users."""

import pytest
from httpx import AsyncClient

from tests.conftest import sign_in

pytestmark = pytest.mark.db

PROTECTED_GETS = [
    "/api/challenges",
    "/api/challenges/url-shortener",
    "/api/concepts",
    "/api/concepts/qps",
    "/api/progress",
    "/api/progress/skills",
    "/api/progress/recommendations",
    "/api/users/me",
]


@pytest.mark.parametrize("url", PROTECTED_GETS)
async def test_protected_endpoints_require_a_session(api: AsyncClient, url):
    api.cookies.clear()
    assert (await api.get(url)).status_code == 401


async def test_state_changing_requests_require_the_csrf_token(session):
    response = await session.client.post(
        "/api/challenges/url-shortener/attempts", json={"mode": "practice"}
    )
    assert response.status_code == 403


async def test_a_user_cannot_read_another_users_attempt(api: AsyncClient):
    api.cookies.clear()
    first = await sign_in(api, "owner@napkinchain.app")
    await first.post("/api/challenges/url-shortener/attempts", json={"mode": "practice"})
    await first.post(
        "/api/challenges/url-shortener/nodes/write_qps/estimate",
        json={"estimate": 1000, "timeSpentSeconds": 10},
    )

    api.cookies.clear()
    other = await sign_in(api, "intruder@napkinchain.app")
    await other.delete("/api/users/me/progress")

    # The other user has no attempt of their own, and cannot see the first one.
    assert (await other.get("/api/challenges/url-shortener/progress")).status_code == 404
    api.cookies.clear()


async def test_the_client_cannot_choose_its_own_user_id(session):
    await session.post("/api/challenges/url-shortener/attempts", json={"mode": "practice"})
    response = await session.post(
        "/api/challenges/url-shortener/nodes/write_qps/estimate",
        json={"estimate": 1000, "userId": "000000000000000000000000", "ratio": 1.0},
    )
    assert response.status_code == 200
    # The submitted ratio was ignored; the server computed its own.
    assert response.json()["feedback"]["ratio"] == 1.0

    result = await session.get("/api/challenges/url-shortener/progress")
    assert result.status_code == 200


async def test_expected_answers_are_not_disclosed_before_answering(session):
    state = await session.post(
        "/api/challenges/instagram-feed/attempts", json={"mode": "practice"}
    )
    body = state.text
    assert "expectedMin" not in body
    assert "expectedValue" not in body
    assert "explanationSteps" not in body

    question = await session.get("/api/challenges/instagram-feed/nodes/actions_day")
    assert question.status_code == 200
    assert "expected" not in question.text


async def test_hints_are_revealed_one_at_a_time(session):
    await session.post("/api/challenges/instagram-feed/attempts", json={"mode": "practice"})
    question = (await session.get("/api/challenges/instagram-feed/nodes/actions_day")).json()
    assert question["hints"] == []
    assert question["hintsAvailable"] == 2

    first = (await session.post(
        "/api/challenges/instagram-feed/nodes/actions_day/hint"
    )).json()
    assert first["hintsRevealed"] == 1
    question = (await session.get("/api/challenges/instagram-feed/nodes/actions_day")).json()
    assert len(question["hints"]) == 1


async def test_hints_are_unavailable_in_interview_mode(session):
    await session.post(
        "/api/challenges/instagram-feed/attempts", json={"mode": "interview", "restart": True}
    )
    response = await session.post("/api/challenges/instagram-feed/nodes/actions_day/hint")
    assert response.status_code == 403


async def test_locked_steps_cannot_be_answered(session):
    await session.post("/api/challenges/instagram-feed/attempts", json={"mode": "practice"})
    response = await session.post(
        "/api/challenges/instagram-feed/nodes/servers/estimate",
        json={"estimate": 50, "timeSpentSeconds": 5},
    )
    assert response.status_code == 409


async def test_estimates_must_be_positive(session):
    await session.post("/api/challenges/url-shortener/attempts", json={"mode": "practice"})
    response = await session.post(
        "/api/challenges/url-shortener/nodes/write_qps/estimate",
        json={"estimate": -5},
    )
    assert response.status_code == 422
