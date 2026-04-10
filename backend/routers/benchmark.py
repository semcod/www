"""Benchmark KPI router — cases, feedback, decisions, events, export, summary."""
import csv
import io
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from db_module import (
    create_benchmark_case,
    get_benchmark_cases,
    get_benchmark_case,
    update_benchmark_case,
    create_benchmark_event,
    get_benchmark_events,
    upsert_recommendation_feedback,
    get_feedback_for_case,
    get_benchmark_summary,
)

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    case_id: str
    repo: str
    audit_id: Optional[str] = None
    source_type: str = "repo"
    change_type: str = ""
    baseline_tools: List[str] = []
    baseline_findings: str = ""
    baseline_detected: bool = False
    pr_reference: str = ""
    ticket_id: str = ""
    benchmark_mode: bool = True


class CaseUpdate(BaseModel):
    audit_id: Optional[str] = None
    reviewer_verdict: Optional[str] = None
    recommendation_accepted: Optional[bool] = None
    pr_candidate: Optional[bool] = None
    deployment_candidate: Optional[bool] = None
    deployment_model_selected: Optional[str] = None
    time_to_first_result_seconds: Optional[int] = None
    time_to_first_useful_recommendation_seconds: Optional[int] = None
    next_action: Optional[str] = None


class DecisionPayload(BaseModel):
    pr_candidate: Optional[bool] = None
    deployment_candidate: Optional[bool] = None
    deployment_model_selected: Optional[str] = None
    reviewer_verdict: Optional[str] = None
    next_action: Optional[str] = None


class FeedbackPayload(BaseModel):
    audit_id: Optional[str] = None
    accepted: Optional[bool] = None
    novelty_score: Optional[int] = None
    usefulness_score: Optional[int] = None
    accuracy_score: Optional[int] = None
    actionability_score: Optional[int] = None
    business_value_score: Optional[int] = None
    notes: str = ""


class EventPayload(BaseModel):
    event_name: str
    event_value: str = ""
    audit_id: Optional[str] = None
    metadata: Dict = {}


# ─── Cases ────────────────────────────────────────────────────────────────────

@router.post("/cases", status_code=201)
def post_case(body: CaseCreate):
    existing = get_benchmark_case(body.case_id)
    if existing:
        raise HTTPException(409, f"Case {body.case_id} already exists")
    return create_benchmark_case(body.model_dump())


@router.get("/cases")
def list_cases():
    return {"cases": get_benchmark_cases()}


@router.get("/cases/{case_id}")
def get_case(case_id: str):
    case = get_benchmark_case(case_id)
    if not case:
        raise HTTPException(404, f"Case {case_id} not found")
    return case


@router.patch("/cases/{case_id}")
def patch_case(case_id: str, body: CaseUpdate):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    result = update_benchmark_case(case_id, updates)
    if not result:
        raise HTTPException(404, f"Case {case_id} not found")
    return result


# ─── Decision ─────────────────────────────────────────────────────────────────

@router.post("/cases/{case_id}/decision")
def post_decision(case_id: str, body: DecisionPayload):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    result = update_benchmark_case(case_id, updates)
    if not result:
        raise HTTPException(404, f"Case {case_id} not found")
    return result


# ─── Recommendation Feedback ──────────────────────────────────────────────────

@router.post("/cases/{case_id}/recommendations/{recommendation_id}/feedback")
def post_feedback(case_id: str, recommendation_id: str, body: FeedbackPayload):
    if not get_benchmark_case(case_id):
        raise HTTPException(404, f"Case {case_id} not found")
    return upsert_recommendation_feedback(case_id, recommendation_id, body.model_dump())


@router.get("/cases/{case_id}/recommendations/feedback")
def list_feedback(case_id: str):
    if not get_benchmark_case(case_id):
        raise HTTPException(404, f"Case {case_id} not found")
    return {"feedback": get_feedback_for_case(case_id)}


# ─── Events ───────────────────────────────────────────────────────────────────

@router.post("/cases/{case_id}/events", status_code=201)
def post_event(case_id: str, body: EventPayload):
    if not get_benchmark_case(case_id):
        raise HTTPException(404, f"Case {case_id} not found")
    return create_benchmark_event(case_id, body.model_dump())


@router.get("/cases/{case_id}/events")
def list_events(case_id: str):
    if not get_benchmark_case(case_id):
        raise HTTPException(404, f"Case {case_id} not found")
    return {"events": get_benchmark_events(case_id)}


# ─── Summary ──────────────────────────────────────────────────────────────────

@router.get("/summary")
def summary():
    return get_benchmark_summary()


# ─── Export ───────────────────────────────────────────────────────────────────

@router.get("/export.json")
def export_json():
    cases = get_benchmark_cases()
    for c in cases:
        c["feedback"] = get_feedback_for_case(c["case_id"])
        c["events"] = get_benchmark_events(c["case_id"])
    return {"cases": cases, "summary": get_benchmark_summary()}


@router.get("/export.csv")
def export_csv():
    cases = get_benchmark_cases()
    if not cases:
        return StreamingResponse(io.StringIO(""), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=benchmark.csv"})
    fields = [
        "case_id", "repo", "source_type", "change_type", "baseline_detected",
        "reviewer_verdict", "recommendation_accepted", "pr_candidate",
        "deployment_candidate", "deployment_model_selected",
        "time_to_first_result_seconds", "time_to_first_useful_recommendation_seconds",
        "next_action", "created_at",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for c in cases:
        writer.writerow(c)
    buf.seek(0)
    return StreamingResponse(buf, media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=benchmark.csv"})
