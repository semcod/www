from typing import Optional

from fastapi import APIRouter
from fastapi.responses import Response

from store import badge_cache

router = APIRouter()


@router.get("/badge/{repo_slug}.svg")
async def health_badge(repo_slug: str, style: str = "flat"):
    """
    Generate SVG badge with code health score.

    Usage in README:
    ![Code Health](https://semcod.com/badge/owner-repo.svg)

    repo_slug format: "owner-repo" (dashes instead of slash)
    """
    repo = repo_slug.replace("-", "/", 1)
    cached = badge_cache.get(repo)

    if cached:
        score = cached["score"]
        grade = cached["grade"]
        weekly_issues = cached.get("weekly_issues")
    else:
        score = None
        grade = "?"
        weekly_issues = None

    svg = _generate_badge_svg(grade, score, style, weekly_issues)
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "ETag": f'"{grade}-{score}"',
        },
    )


def _generate_badge_svg(grade: str, score: Optional[int], style: str, weekly_issues: Optional[int] = None) -> str:
    """Generate shields.io-style SVG badge."""
    colors = {
        "A+": "#22c55e", "A": "#34d399", "B+": "#a3e635",
        "B": "#facc15", "C": "#fb923c", "D": "#f87171",
        "F": "#ef4444", "?": "#94a3b8",
    }
    color = colors.get(grade, "#94a3b8")

    if weekly_issues is not None and weekly_issues > 0:
        label = f"{weekly_issues} issues prevented"
        value = "this week"
    elif weekly_issues == 0:
        label = "AI review"
        value = "active"
    else:
        label = "code health"
        value = f"{grade}" if score is None else f"{grade} · {score}%"

    label_width = len(label) * 6.5 + 12
    value_width = len(value) * 7 + 12
    total_width = label_width + value_width

    svg = f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{total_width}\" height=\"20\" role=\"img\" aria-label=\"{label}: {value}\">
  <title>{label}: {value}</title>
  <linearGradient id=\"s\" x2=\"0\" y2=\"100%\">
    <stop offset=\"0\" stop-color=\"#bbb\" stop-opacity=\".1\"/>
    <stop offset=\"1\" stop-opacity=\".1\"/>
  </linearGradient>
  <clipPath id=\"r\">
    <rect width=\"{total_width}\" height=\"20\" rx=\"3\" fill=\"#fff\"/>
  </clipPath>
  <g clip-path=\"url(#r)\">
    <rect width=\"{label_width}\" height=\"20\" fill=\"#555\"/>
    <rect x=\"{label_width}\" width=\"{value_width}\" height=\"20\" fill=\"{color}\"/>
    <rect width=\"{total_width}\" height=\"20\" fill=\"url(#s)\"/>
  </g>
  <g fill=\"#fff\" text-anchor=\"middle\" font-family=\"Verdana,Geneva,DejaVu Sans,sans-serif\" text-rendering=\"geometricPrecision\" font-size=\"11\">
    <text aria-hidden=\"true\" x=\"{label_width/2}\" y=\"15\" fill=\"#010101\" fill-opacity=\".3\">{label}</text>
    <text x=\"{label_width/2}\" y=\"14\">{label}</text>
    <text aria-hidden=\"true\" x=\"{label_width + value_width/2}\" y=\"15\" fill=\"#010101\" fill-opacity=\".3\">{value}</text>
    <text x=\"{label_width + value_width/2}\" y=\"14\">{value}</text>
  </g>
</svg>"""
    return svg
