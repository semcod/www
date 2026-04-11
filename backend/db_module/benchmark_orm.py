"""Benchmark CRUD operations using SQLAlchemy ORM."""
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from db_models import BenchmarkCase, BenchmarkEvent, RecommendationFeedback


# ─── BenchmarkCase ────────────────────────────────────────────────────────────

def create_benchmark_case(db: Session, payload: Dict) -> Dict:
    case = BenchmarkCase(
        case_id=payload["case_id"],
        audit_id=payload.get("audit_id"),
        repo=payload["repo"],
        source_type=payload.get("source_type", "repo"),
        change_type=payload.get("change_type", ""),
        baseline_tools=json.dumps(payload.get("baseline_tools", [])),
        baseline_findings=payload.get("baseline_findings", ""),
        baseline_detected=payload.get("baseline_detected", False),
        pr_reference=payload.get("pr_reference", ""),
        ticket_id=payload.get("ticket_id", ""),
        benchmark_mode=payload.get("benchmark_mode", True),
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return _case_to_dict(case)


def get_benchmark_cases(db: Session) -> List[Dict]:
    rows = db.execute(select(BenchmarkCase).order_by(BenchmarkCase.created_at.desc())).scalars().all()
    return [_case_to_dict(r) for r in rows]


def get_benchmark_case(db: Session, case_id: str) -> Optional[Dict]:
    row = db.execute(select(BenchmarkCase).where(BenchmarkCase.case_id == case_id)).scalar_one_or_none()
    return _case_to_dict(row) if row else None


def update_benchmark_case(db: Session, case_id: str, updates: Dict) -> Optional[Dict]:
    row = db.execute(select(BenchmarkCase).where(BenchmarkCase.case_id == case_id)).scalar_one_or_none()
    if not row:
        return None
    for k, v in updates.items():
        if hasattr(row, k):
            setattr(row, k, v)
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return _case_to_dict(row)


def _case_to_dict(c: BenchmarkCase) -> Dict:
    return {
        "case_id": c.case_id,
        "audit_id": c.audit_id,
        "repo": c.repo,
        "source_type": c.source_type,
        "change_type": c.change_type,
        "baseline_tools": json.loads(c.baseline_tools or "[]"),
        "baseline_findings": c.baseline_findings,
        "baseline_detected": c.baseline_detected,
        "reviewer_verdict": c.reviewer_verdict,
        "recommendation_accepted": c.recommendation_accepted,
        "pr_candidate": c.pr_candidate,
        "deployment_candidate": c.deployment_candidate,
        "deployment_model_selected": c.deployment_model_selected,
        "pr_reference": c.pr_reference,
        "ticket_id": c.ticket_id,
        "benchmark_mode": c.benchmark_mode,
        "time_to_first_result_seconds": c.time_to_first_result_seconds,
        "time_to_first_useful_recommendation_seconds": c.time_to_first_useful_recommendation_seconds,
        "next_action": c.next_action,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


# ─── BenchmarkEvent ───────────────────────────────────────────────────────────

def create_benchmark_event(db: Session, case_id: str, payload: Dict) -> Dict:
    ev = BenchmarkEvent(
        case_id=case_id,
        audit_id=payload.get("audit_id"),
        event_name=payload["event_name"],
        event_value=payload.get("event_value", ""),
        metadata_json=json.dumps(payload.get("metadata", {})),
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return _event_to_dict(ev)


def _event_to_dict(ev: BenchmarkEvent) -> Dict:
    return {
        "id": ev.id,
        "case_id": ev.case_id,
        "audit_id": ev.audit_id,
        "event_name": ev.event_name,
        "event_value": ev.event_value,
        "metadata": json.loads(ev.metadata_json or "{}"),
        "created_at": ev.created_at.isoformat() if ev.created_at else None,
    }


def get_benchmark_events(db: Session, case_id: str) -> List[Dict]:
    rows = db.execute(
        select(BenchmarkEvent).where(BenchmarkEvent.case_id == case_id).order_by(BenchmarkEvent.created_at.asc())
    ).scalars().all()
    return [_event_to_dict(r) for r in rows]


# ─── RecommendationFeedback ───────────────────────────────────────────────────

def upsert_recommendation_feedback(db: Session, case_id: str, recommendation_id: str, payload: Dict) -> Dict:
    row = db.execute(
        select(RecommendationFeedback).where(
            RecommendationFeedback.case_id == case_id,
            RecommendationFeedback.recommendation_id == recommendation_id,
        )
    ).scalar_one_or_none()

    if row:
        _update_feedback_fields(row, payload)
    else:
        row = _build_feedback_row(case_id, recommendation_id, payload)
        db.add(row)

    db.commit()
    db.refresh(row)
    return _feedback_to_dict(row)


_FEEDBACK_FIELDS = ("accepted", "novelty_score", "usefulness_score", "accuracy_score",
                    "actionability_score", "business_value_score", "notes")


def _update_feedback_fields(row: RecommendationFeedback, payload: Dict) -> None:
    for k in _FEEDBACK_FIELDS:
        if k in payload and payload[k] is not None:
            setattr(row, k, payload[k])


def _build_feedback_row(case_id: str, recommendation_id: str, payload: Dict) -> RecommendationFeedback:
    return RecommendationFeedback(
        case_id=case_id,
        audit_id=payload.get("audit_id"),
        recommendation_id=recommendation_id,
        accepted=payload.get("accepted"),
        novelty_score=payload.get("novelty_score"),
        usefulness_score=payload.get("usefulness_score"),
        accuracy_score=payload.get("accuracy_score"),
        actionability_score=payload.get("actionability_score"),
        business_value_score=payload.get("business_value_score"),
        notes=payload.get("notes", ""),
    )


def get_feedback_for_case(db: Session, case_id: str) -> List[Dict]:
    rows = db.execute(
        select(RecommendationFeedback).where(RecommendationFeedback.case_id == case_id)
    ).scalars().all()
    return [_feedback_to_dict(r) for r in rows]


def _feedback_to_dict(f: RecommendationFeedback) -> Dict:
    return {
        "id": f.id,
        "case_id": f.case_id,
        "audit_id": f.audit_id,
        "recommendation_id": f.recommendation_id,
        "accepted": f.accepted,
        "novelty_score": f.novelty_score,
        "usefulness_score": f.usefulness_score,
        "accuracy_score": f.accuracy_score,
        "actionability_score": f.actionability_score,
        "business_value_score": f.business_value_score,
        "notes": f.notes,
        "created_at": f.created_at.isoformat() if f.created_at else None,
    }


# ─── Summary ──────────────────────────────────────────────────────────────────

def get_benchmark_summary(db: Session) -> Dict:
    total = db.execute(select(func.count(BenchmarkCase.id))).scalar() or 0
    pr_candidates = db.execute(
        select(func.count(BenchmarkCase.id)).where(BenchmarkCase.pr_candidate == True)
    ).scalar() or 0
    deployment_decisions = db.execute(
        select(func.count(BenchmarkCase.id)).where(BenchmarkCase.deployment_model_selected != "")
    ).scalar() or 0

    feedback_rows = db.execute(select(RecommendationFeedback)).scalars().all()
    fb_stats = _compute_feedback_stats(feedback_rows)

    return {
        "total_cases": total,
        "pr_conversion_rate": round(pr_candidates / total, 3) if total else 0,
        "deployment_decision_rate": round(deployment_decisions / total, 3) if total else 0,
        **fb_stats,
    }


def _compute_feedback_stats(feedback_rows: list) -> Dict:
    total_fb = len(feedback_rows)
    accepted = sum(1 for f in feedback_rows if f.accepted)
    novelty_scores = [f.novelty_score for f in feedback_rows if f.novelty_score is not None]
    novel_high = sum(1 for s in novelty_scores if s >= 2)

    return {
        "total_feedback": total_fb,
        "recommendation_acceptance_rate": round(accepted / total_fb, 3) if total_fb else 0,
        "novel_actionable_finding_rate": round(novel_high / len(novelty_scores), 3) if novelty_scores else 0,
    }
