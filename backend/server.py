"""
Semcod GitHub App — Backend
===========================
One-click Audit + PR Comment Bot + Code Health Badge

Deploy: uvicorn server:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import FRONTEND_URL
from routers.auth import router as auth_router
from routers.audit import router as audit_router
from routers.webhook import router as webhook_router
from routers.badge import router as badge_router
from routers.report import router as report_router
from store import audit_results, badge_cache

# ─── Config ───────────────────────────────────────────────────────────────────

app = FastAPI(title="Semcod", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://semcod.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(webhook_router)
app.include_router(badge_router)
app.include_router(report_router)


# ─── Health check ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "tools": ["code2llm", "redup", "pyqual", "regix", "vallm"],
        "audits_cached": len(audit_results),
        "badges_cached": len(badge_cache),
    }


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
