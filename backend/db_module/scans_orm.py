"""Scan-related database operations using SQLAlchemy ORM."""
import json
from typing import List, Dict, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from db_models import Scan, AuditResult, BadgeCache


def save_scan(db: Session, scan_data: Dict) -> int:
    """Save a scan to the database."""
    scan = Scan(
        repo=scan_data["repo"],
        health_score=scan_data["health_score"],
        grade=scan_data["grade"],
        stats=json.dumps(scan_data["stats"]),
        completed=scan_data["completed"],
        sandbox=1 if scan_data.get("sandbox") else 0,
        badge_url=scan_data.get("badge_url", ""),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan.id


def get_recent_scans(db: Session, limit: int = 100) -> List[Dict]:
    """Get recent scans from the database."""
    stmt = select(Scan).order_by(Scan.created_at.desc()).limit(limit)
    result = db.execute(stmt).scalars().all()
    
    scans = []
    for scan in result:
        scans.append({
            "repo": scan.repo,
            "health_score": scan.health_score,
            "grade": scan.grade,
            "stats": json.loads(scan.stats) if scan.stats else {},
            "completed": scan.completed,
            "sandbox": bool(scan.sandbox),
            "badge_url": scan.badge_url,
        })
    return scans


def get_repo_scans(db: Session, repo: str, limit: int = 100) -> List[Dict]:
    """Get scans for a specific repository ordered by date ascending."""
    stmt = (
        select(Scan)
        .where(Scan.repo == repo)
        .order_by(Scan.created_at.asc())
        .limit(limit)
    )
    result = db.execute(stmt).scalars().all()
    
    return [
        {
            "repo": scan.repo,
            "health_score": scan.health_score,
            "grade": scan.grade,
            "stats": json.loads(scan.stats) if scan.stats else {},
            "completed": scan.completed,
            "sandbox": bool(scan.sandbox),
            "badge_url": scan.badge_url,
        }
        for scan in result
    ]


def get_total_scan_count(db: Session) -> int:
    """Get total number of scans in the database."""
    stmt = select(func.count(Scan.id))
    result = db.execute(stmt).scalar()
    return result or 0


def save_audit_result(db: Session, audit_id: str, audit_data: Dict) -> None:
    """Save audit result to database."""
    audit = db.query(AuditResult).filter(AuditResult.audit_id == audit_id).first()
    
    if audit:
        # Update existing
        audit.repo = audit_data.get("repo")
        audit.status = audit_data.get("status")
        audit.started = audit_data.get("started")
        audit.completed = audit_data.get("completed")
        audit.health_score = audit_data.get("health_score")
        audit.grade = audit_data.get("grade")
        audit.stats = json.dumps(audit_data.get("stats", {}))
        audit.metrics = json.dumps(audit_data.get("metrics", {}))
        audit.recommendations = json.dumps(audit_data.get("recommendations", []))
        audit.error = audit_data.get("error")
    else:
        # Create new
        audit = AuditResult(
            audit_id=audit_id,
            repo=audit_data.get("repo"),
            status=audit_data.get("status"),
            started=audit_data.get("started"),
            completed=audit_data.get("completed"),
            health_score=audit_data.get("health_score"),
            grade=audit_data.get("grade"),
            stats=json.dumps(audit_data.get("stats", {})),
            metrics=json.dumps(audit_data.get("metrics", {})),
            recommendations=json.dumps(audit_data.get("recommendations", [])),
            error=audit_data.get("error"),
        )
        db.add(audit)
    
    db.commit()


def get_audit_result(db: Session, audit_id: str) -> Optional[Dict]:
    """Get audit result from database."""
    stmt = select(AuditResult).where(AuditResult.audit_id == audit_id)
    audit = db.execute(stmt).scalar_one_or_none()
    
    if not audit:
        return None
    
    return {
        "audit_id": audit.audit_id,
        "repo": audit.repo,
        "status": audit.status,
        "started": audit.started,
        "completed": audit.completed,
        "health_score": audit.health_score,
        "grade": audit.grade,
        "stats": json.loads(audit.stats) if audit.stats else {},
        "metrics": json.loads(audit.metrics) if audit.metrics else {},
        "recommendations": json.loads(audit.recommendations) if audit.recommendations else [],
        "error": audit.error,
    }


def save_badge_cache(db: Session, repo: str, badge_data: Dict) -> None:
    """Save badge cache to database."""
    badge = db.query(BadgeCache).filter(BadgeCache.repo == repo).first()
    
    if badge:
        # Update existing
        badge.score = badge_data.get("score")
        badge.grade = badge_data.get("grade")
        badge.updated = badge_data.get("updated")
        badge.weekly_issues = badge_data.get("weekly_issues", 0)
    else:
        # Create new
        badge = BadgeCache(
            repo=repo,
            score=badge_data.get("score"),
            grade=badge_data.get("grade"),
            updated=badge_data.get("updated"),
            weekly_issues=badge_data.get("weekly_issues", 0),
        )
        db.add(badge)
    
    db.commit()


def get_badge_cache(db: Session, repo: str) -> Optional[Dict]:
    """Get badge cache from database."""
    stmt = select(BadgeCache).where(BadgeCache.repo == repo)
    badge = db.execute(stmt).scalar_one_or_none()
    
    if not badge:
        return None
    
    return {
        "repo": badge.repo,
        "score": badge.score,
        "grade": badge.grade,
        "updated": badge.updated,
        "weekly_issues": badge.weekly_issues,
    }
