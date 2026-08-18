"""The flow the whole product exists to support:

start -> solve -> fail a step -> learn the concept -> return to that exact
step -> retry -> succeed -> finish the chain -> see results.
"""

import pytest

pytestmark = pytest.mark.db

SLUG = "instagram-feed"
GOOD_ANSWERS = {
    "actions_day": 1_000_000_000,
    "avg_qps": 10_000,
    "peak_qps": 30_000,
    "peak_bandwidth": 6,
    "storage_day": 15,
    "storage_5y": 90,
    "servers": 50,
}


async def estimate(session, node_id: str, value: float, **extra):
    return await session.post(
        f"/api/challenges/{SLUG}/nodes/{node_id}/estimate",
        json={"estimate": value, "timeSpentSeconds": 30, **extra},
    )


async def test_the_full_learning_loop(session):
    # 1. Start the chain.
    state = (await session.post(f"/api/challenges/{SLUG}/attempts", json={"mode": "practice"})).json()
    assert state["currentNodeId"] == "actions_day"
    assert state["solvedCount"] == 0
    assert state["totalSteps"] == 7

    statuses = {n["id"]: n["status"] for n in state["chain"]}
    assert statuses["dau"] == "solved"        # an input, given for free
    assert statuses["actions_day"] == "active"
    assert statuses["avg_qps"] == "locked"    # depends on actions_day
    assert statuses["storage_day"] == "available"  # a parallel branch off dau

    # 2. Solve the first step well.
    first = (await estimate(session, "actions_day", 1_000_000_000)).json()
    assert first["feedback"]["classification"] == "excellent"
    assert first["feedback"]["nodeStatus"] == "mastered"
    assert first["unlockedNodeIds"] == ["avg_qps"]
    assert first["state"]["currentNodeId"] == "avg_qps"

    # 3. Get the next step badly wrong.
    failed = (await estimate(session, "avg_qps", 400_000)).json()
    feedback = failed["feedback"]
    assert feedback["classification"] == "needs_review"
    assert feedback["passed"] is False
    assert feedback["nodeStatus"] == "weak"
    assert feedback["ratio"] > 10
    assert feedback["conceptId"] == "qps"
    assert feedback["explanationSteps"]  # the "why" is shown after answering
    assert feedback["shortcut"] == "1 day ~ 100K seconds"

    # The chain moves on rather than blocking - a weak node still unlocks.
    assert failed["state"]["currentNodeId"] == "peak_qps"

    # 4. Go and learn the concept the step depends on.
    concept = (await session.get(f"/api/concepts/{feedback['conceptId']}")).json()
    assert concept["title"] == "Requests/day to QPS"
    assert concept["shortcut"]
    assert concept["examples"]

    learned = (await session.post(f"/api/concepts/{feedback['conceptId']}/learned")).json()
    assert learned["learned"] is True

    # 5. Come straight back to that exact step.
    retried = (await session.post(f"/api/challenges/{SLUG}/nodes/avg_qps/retry")).json()
    assert retried["currentNodeId"] == "avg_qps"
    assert retried["question"]["id"] == "avg_qps"
    assert retried["question"]["attempts"] == 1  # the history is not erased

    # 6. Retry it and succeed.
    second = (await estimate(session, "avg_qps", 10_000)).json()
    assert second["feedback"]["passed"] is True
    assert second["feedback"]["nodeStatus"] == "solved"  # earned on retry, not mastered

    # 7. Finish the rest of the chain.
    for node_id in ("peak_qps", "peak_bandwidth", "storage_day", "storage_5y", "servers"):
        response = (await estimate(session, node_id, GOOD_ANSWERS[node_id])).json()
        assert response["feedback"]["passed"] is True
    assert response["challengeCompleted"] is True
    assert response["state"]["status"] == "completed"

    # 8. See the results.
    result = (await session.get(f"/api/challenges/{SLUG}/result")).json()
    assert result["solvedCount"] == 7
    assert result["totalSteps"] == 7
    assert result["weakCount"] == 0
    assert result["score"] == 1.0
    assert result["averageRatio"] == 1.0
    assert {n["nodeId"] for n in result["nodes"]} == set(GOOD_ANSWERS)

    # 9. The concept the user struggled with is now tracked.
    skills = (await session.get("/api/progress/skills")).json()
    qps = next(c for c in skills["concepts"] if c["conceptId"] == "qps")
    assert qps["attempts"] == 2
    assert qps["learned"] is True


async def test_progress_is_resumable(session):
    await session.post(f"/api/challenges/{SLUG}/attempts", json={"mode": "practice"})
    await estimate(session, "actions_day", 1_000_000_000)

    # Simulate leaving and coming back.
    resumed = (await session.post(f"/api/challenges/{SLUG}/resume")).json()
    assert resumed["currentNodeId"] == "avg_qps"
    assert resumed["solvedCount"] == 1

    home = (await session.get("/api/progress/home")).json()
    assert home["continueCard"]["challengeSlug"] == SLUG
    assert home["continueCard"]["solvedCount"] == 1


async def test_restarting_abandons_the_previous_attempt(session):
    await session.post(f"/api/challenges/{SLUG}/attempts", json={"mode": "practice"})
    await estimate(session, "actions_day", 1_000_000_000)

    restarted = (await session.post(
        f"/api/challenges/{SLUG}/attempts", json={"mode": "learn", "restart": True}
    )).json()
    assert restarted["solvedCount"] == 0
    assert restarted["currentNodeId"] == "actions_day"
    assert restarted["mode"] == "learn"


async def test_rough_work_is_persisted_with_the_estimate(session):
    await session.post(f"/api/challenges/{SLUG}/attempts", json={"mode": "learn"})
    await estimate(session, "actions_day", 1_000_000_000, calculation="100M x 10 = 1B")

    await session.post(f"/api/challenges/{SLUG}/nodes/avg_qps/retry")
    question = (await session.get(f"/api/challenges/{SLUG}/nodes/actions_day")).json()
    assert question["lastCalculation"] == "100M x 10 = 1B"


async def test_unsubmitted_calculations_survive_a_reload(session):
    await session.post(f"/api/challenges/{SLUG}/attempts", json={"mode": "practice"})
    await session.post(
        f"/api/challenges/{SLUG}/nodes/actions_day/draft",
        json={"calculation": "100M users, maybe 10 opens?"},
    )
    state = (await session.get(f"/api/challenges/{SLUG}/progress")).json()
    assert state["question"]["lastCalculation"] == "100M users, maybe 10 opens?"


async def test_a_weak_step_surfaces_in_the_result_and_in_recommendations(session):
    await session.post(f"/api/challenges/url-shortener/attempts", json={"mode": "practice"})
    await session.post(
        "/api/challenges/url-shortener/nodes/write_qps/estimate",
        json={"estimate": 50_000, "timeSpentSeconds": 20},
    )
    await session.post(
        "/api/challenges/url-shortener/nodes/read_qps/estimate",
        json={"estimate": 900_000, "timeSpentSeconds": 20},
    )

    result = (await session.get("/api/challenges/url-shortener/result")).json()
    assert result["weakCount"] == 2
    assert set(result["weakConceptIds"]) == {"qps", "read-write-ratio"}

    # Two poor attempts on a concept are enough to be recommended it.
    await session.post(
        "/api/challenges/url-shortener/nodes/write_qps/retry"
    )
    await session.post(
        "/api/challenges/url-shortener/nodes/write_qps/estimate",
        json={"estimate": 60_000, "timeSpentSeconds": 20},
    )
    recommendations = (await session.get("/api/progress/recommendations")).json()
    assert any(r["conceptId"] == "qps" for r in recommendations)


async def test_practising_a_concept_drill_moves_mastery(session):
    before = (await session.get("/api/concepts/qps")).json()
    assert before["mastery"] == 0.0

    drill = (await session.post(
        "/api/concepts/qps/practice", json={"estimate": 500, "timeSpentSeconds": 25}
    )).json()
    assert drill["passed"] is True
    assert drill["mastery"] > 0
    assert drill["explanation"]

    after = (await session.get("/api/concepts/qps")).json()
    assert after["mastery"] == drill["mastery"]


async def test_the_concept_library_is_grouped_by_area(session):
    groups = (await session.get("/api/concepts")).json()
    areas = [g["area"] for g in groups]
    assert areas == ["traffic", "storage", "bandwidth", "capacity"]
    assert sum(len(g["concepts"]) for g in groups) == 8
