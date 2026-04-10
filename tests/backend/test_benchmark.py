"""Benchmark router tests."""
import time
import pytest

_TS = str(int(time.time() * 1000))[-6:]

pytestmark = [pytest.mark.fast, pytest.mark.unit]


def test_benchmark_summary_empty(client):
    resp = client.get("/api/benchmark/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_cases" in data
    assert "pr_conversion_rate" in data
    assert "recommendation_acceptance_rate" in data


def test_create_and_get_case(client):
    payload = {
        "case_id": f"BM-TEST-{_TS}-001",
        "repo": "owner/repo",
        "source_type": "pr",
        "change_type": "bugfix",
        "baseline_detected": True,
        "baseline_tools": ["ruff", "ci"],
    }
    resp = client.post("/api/benchmark/cases", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "BM-TEST-" in data["case_id"]
    assert data["source_type"] == "pr"

    resp = client.get("/api/benchmark/cases/BM-TEST-001")
    assert resp.status_code == 200
    assert resp.json()["repo"] == "owner/repo"


def test_duplicate_case_rejected(client):
    payload = {"case_id": "BM-DUP-001", "repo": "x/y"}
    client.post("/api/benchmark/cases", json=payload)
    resp = client.post("/api/benchmark/cases", json=payload)
    assert resp.status_code == 409


def test_patch_case(client):
    client.post("/api/benchmark/cases", json={"case_id": "BM-PATCH-001", "repo": "x/y"})
    resp = client.patch("/api/benchmark/cases/BM-PATCH-001",
                        json={"reviewer_verdict": "go", "pr_candidate": True})
    assert resp.status_code == 200
    assert resp.json()["reviewer_verdict"] == "go"
    assert resp.json()["pr_candidate"] is True


def test_post_decision(client):
    client.post("/api/benchmark/cases", json={"case_id": "BM-DEC-001", "repo": "x/y"})
    resp = client.post("/api/benchmark/cases/BM-DEC-001/decision",
                       json={"deployment_model_selected": "hybrid", "pr_candidate": True})
    assert resp.status_code == 200
    assert resp.json()["deployment_model_selected"] == "hybrid"


def test_post_feedback(client):
    client.post("/api/benchmark/cases", json={"case_id": "BM-FB-001", "repo": "x/y"})
    resp = client.post(
        "/api/benchmark/cases/BM-FB-001/recommendations/rec123abc/feedback",
        json={"accepted": True, "novelty_score": 3, "usefulness_score": 2, "notes": "Good"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["accepted"] is True
    assert data["novelty_score"] == 3


def test_post_event(client):
    client.post("/api/benchmark/cases", json={"case_id": "BM-EV-001", "repo": "x/y"})
    resp = client.post("/api/benchmark/cases/BM-EV-001/events",
                       json={"event_name": "result_viewed", "audit_id": "abc123"})
    assert resp.status_code == 201
    assert resp.json()["event_name"] == "result_viewed"


def test_export_csv_empty(client):
    resp = client.get("/api/benchmark/export.csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


def test_export_json(client):
    resp = client.get("/api/benchmark/export.json")
    assert resp.status_code == 200
    assert "cases" in resp.json()


def test_recommendation_id_in_scoring():
    from services.scoring import generate_recommendations
    recs = generate_recommendations(
        {"cc_avg": 10},
        {"duplication_groups": 0},
        {"errors": 0}
    )
    assert len(recs) > 0
    assert "recommendation_id" in recs[0]
    assert len(recs[0]["recommendation_id"]) == 12
