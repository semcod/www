"""Health score calculation and grading."""


def calculate_health_score(stats, complexity, duplication, quality) -> int:
    """Calculate 0-100 health score from metrics."""
    score = 100

    # Complexity penalty (CC avg > 5 starts losing points)
    cc = complexity.get("cc_avg", 5)
    if cc > 10:
        score -= 30
    elif cc > 7:
        score -= 20
    elif cc > 5:
        score -= 10

    # Duplication penalty
    dup_groups = duplication.get("duplication_groups", 0)
    if dup_groups > 20:
        score -= 20
    elif dup_groups > 10:
        score -= 15
    elif dup_groups > 5:
        score -= 10
    elif dup_groups > 0:
        score -= 5

    # Quality errors penalty
    errors = quality.get("errors", 0)
    warnings = quality.get("warnings", 0)
    score -= min(30, errors * 3 + warnings)

    # Size bonus/penalty (very small repos get less data)
    lines = stats.get("total_lines", 0)
    if lines < 100:
        score = max(score, 50)

    return max(0, min(100, score))


def score_to_grade(score: int) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B+"
    if score >= 60:
        return "B"
    if score >= 50:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def generate_recommendations(complexity, duplication, quality) -> list[dict]:
    """Generate actionable recommendations based on metrics."""
    recs = []

    cc = complexity.get("cc_avg", 0)
    if cc > 7:
        recs.append({
            "priority": "high",
            "category": "complexity",
            "title": "Wysoka złożoność cyklomatyczna",
            "description": f"Średnia CC = {cc:.1f}. Cel: < 5. Rozważ podział złożonych funkcji na mniejsze.",
            "tool": "redsl",
            "action": "redsl refactor --strategy split-complex",
        })

    dup = duplication.get("duplication_groups", 0)
    if dup > 5:
        recoverable = duplication.get("recoverable_lines", 0)
        recs.append({
            "priority": "medium",
            "category": "duplication",
            "title": f"{dup} grup duplikacji ({recoverable} linii do odzyskania)",
            "description": "Zduplikowany kod zwiększa koszt utrzymania. Ekstrakcja wspólnych funkcji.",
            "tool": "redup",
            "action": f"redup plan --top {min(dup, 10)}",
        })

    errors = quality.get("errors", 0)
    if errors > 0:
        recs.append({
            "priority": "high",
            "category": "quality",
            "title": f"{errors} błędów jakości kodu",
            "description": "Błędy statycznej analizy (typy, security, style). Napraw przed merge.",
            "tool": "pyqual",
            "action": "pyqual fix --auto",
        })

    if not recs:
        recs.append({
            "priority": "low",
            "category": "maintenance",
            "title": "Kod w dobrej kondycji",
            "description": "Brak krytycznych problemów. Kontynuuj monitorowanie z weekly scans.",
            "tool": "weekly",
            "action": "weekly analyze",
        })

    return recs
