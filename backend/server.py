"""
Semcod GitHub App — Backend
===========================
One-click Audit + PR Comment Bot + Code Health Badge

Deploy: uvicorn server:app --host 0.0.0.0 --port 9000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from routers.auth import router as auth_router
from routers.audit import router as audit_router
from routers.webhook import router as webhook_router
from routers.badge import router as badge_router
from routers.report import router as report_router
from routers.metrics import router as metrics_router
from routers.mcp import router as mcp_router
from routers.system import router as system_router

# ─── Config ───────────────────────────────────────────────────────────────────

app = FastAPI(title="Semcod", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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
app.include_router(metrics_router)
app.include_router(mcp_router)
app.include_router(system_router)


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT
    uvicorn.run(app, host=HOST, port=PORT)
