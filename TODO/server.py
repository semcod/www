"""
Mock GitHub OAuth + API server for testing Semcod login flow.
Simulates: /login/oauth/authorize, /login/oauth/access_token, /api/v3/user, /api/v3/user/repos
"""
import os
import json
import uuid
import time
import hmac
import hashlib
from urllib.parse import urlencode, parse_qs
from fastapi import FastAPI, Request, Query, Header
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="Mock GitHub OAuth Server")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Simulated users ──────────────────────────────────────────────
MOCK_USERS = {
    "tom-sapletta-com": {
        "id": 5669315,
        "login": "tom-sapletta-com",
        "name": "Tom Sapletta",
        "email": "tom@sapletta.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/5669315?v=4",
        "html_url": "https://github.com/tom-sapletta-com",
        "type": "User",
        "bio": "Architect & Developer",
        "company": "Softreck",
        "location": "Gdańsk, Poland",
        "public_repos": 150,
        "created_at": "2013-10-14T12:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }
}

MOCK_REPOS = {
    "tom-sapletta-com": [
        {"id": 1, "name": "semcod", "full_name": "tom-sapletta-com/semcod", "private": False,
         "description": "Semantic Code Analysis", "language": "Python", "default_branch": "main",
         "html_url": "https://github.com/tom-sapletta-com/semcod",
         "clone_url": "https://github.com/tom-sapletta-com/semcod.git"},
        {"id": 2, "name": "letwhisper", "full_name": "tom-sapletta-com/letwhisper", "private": False,
         "description": "Speech-to-text tool", "language": "Python", "default_branch": "main",
         "html_url": "https://github.com/tom-sapletta-com/letwhisper",
         "clone_url": "https://github.com/tom-sapletta-com/letwhisper.git"},
        {"id": 3, "name": "dialogware", "full_name": "tom-sapletta-com/dialogware", "private": True,
         "description": "Dialog platform", "language": "JavaScript", "default_branch": "main",
         "html_url": "https://github.com/tom-sapletta-com/dialogware",
         "clone_url": "https://github.com/tom-sapletta-com/dialogware.git"},
    ]
}

# ── State: issued codes → tokens ─────────────────────────────────
pending_codes: dict[str, dict] = {}   # code → {login, state, ts}
active_tokens: dict[str, str] = {}    # token → login

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8003")


# ── OAuth endpoints ──────────────────────────────────────────────

@app.get("/login/oauth/authorize")
async def authorize(
    client_id: str = Query(...),
    redirect_uri: str = Query(None),
    scope: str = Query("read:user,repo"),
    state: str = Query(None),
    login: str = Query(None),
):
    """Show a simple login page that lets testers pick a user."""
    users_html = ""
    for ulogin, udata in MOCK_USERS.items():
        users_html += f"""
        <button onclick="doLogin('{ulogin}')"
                style="display:flex;align-items:center;gap:12px;padding:12px 24px;
                       font-size:16px;cursor:pointer;border:1px solid #ccc;border-radius:8px;
                       background:#fff;width:100%;margin-bottom:8px;">
            <img src="{udata['avatar_url']}" width="32" height="32"
                 style="border-radius:50%;" onerror="this.style.display='none'"/>
            <span><strong>{udata['name']}</strong> ({ulogin})</span>
        </button>"""

    redirect = redirect_uri or f"{BACKEND_URL}/auth/callback"
    html = f"""<!DOCTYPE html>
<html><head><title>Mock GitHub Login</title></head>
<body style="font-family:sans-serif;display:flex;justify-content:center;padding-top:60px;background:#f6f8fa;">
<div style="background:#fff;padding:32px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.1);max-width:400px;width:100%;">
    <h2 style="margin-top:0;">🧪 Mock GitHub Login</h2>
    <p style="color:#666;font-size:14px;">Simulation mode — select a test user:</p>
    {users_html}
</div>
<script>
function doLogin(login) {{
    const code = login + '_' + Date.now();
    fetch('/api/_sim/issue-code', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{code: code, login: login, state: '{state or ""}'}})
    }}).then(() => {{
        const params = new URLSearchParams({{code: code}});
        if ('{state or ""}') params.set('state', '{state or ""}');
        window.location = '{redirect}?' + params.toString();
    }});
}}
</script>
</body></html>"""
    return HTMLResponse(html)


@app.post("/api/_sim/issue-code")
async def issue_code(request: Request):
    """Internal endpoint: register an auth code."""
    body = await request.json()
    pending_codes[body["code"]] = {
        "login": body["login"],
        "state": body.get("state", ""),
        "ts": time.time(),
    }
    return {"ok": True}


@app.post("/login/oauth/access_token")
async def access_token(request: Request):
    """Exchange code for access token (mimics GitHub)."""
    body = await request.body()
    # Support both form and JSON
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = dict(parse_qs(body.decode()))
        data = {k: v[0] if isinstance(v, list) else v for k, v in data.items()}

    code = data.get("code", "")
    if code not in pending_codes:
        return JSONResponse({"error": "bad_verification_code"}, status_code=400)

    info = pending_codes.pop(code)
    token = f"gho_mock_{uuid.uuid4().hex[:24]}"
    active_tokens[token] = info["login"]

    accept = request.headers.get("accept", "")
    result = {
        "access_token": token,
        "token_type": "bearer",
        "scope": "read:user,repo",
    }
    if "json" in accept:
        return JSONResponse(result)
    # Default: form-encoded (GitHub default)
    return HTMLResponse(urlencode(result), media_type="application/x-www-form-urlencoded")


# ── API v3 endpoints ─────────────────────────────────────────────

def _get_user(authorization: str | None) -> dict | None:
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").replace("token ", "")
    login = active_tokens.get(token)
    if login and login in MOCK_USERS:
        return MOCK_USERS[login]
    return None


@app.get("/api/v3/user")
@app.get("/user")
async def get_user(authorization: str = Header(None)):
    user = _get_user(authorization)
    if not user:
        return JSONResponse({"message": "Bad credentials"}, status_code=401)
    return user


@app.get("/api/v3/user/repos")
@app.get("/user/repos")
async def get_repos(
    authorization: str = Header(None),
    per_page: int = Query(30),
    page: int = Query(1),
    sort: str = Query("updated"),
):
    user = _get_user(authorization)
    if not user:
        return JSONResponse({"message": "Bad credentials"}, status_code=401)
    repos = MOCK_REPOS.get(user["login"], [])
    start = (page - 1) * per_page
    return repos[start : start + per_page]


# ── Health ───────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mode": "github-simulation",
        "users": list(MOCK_USERS.keys()),
        "active_tokens": len(active_tokens),
        "pending_codes": len(pending_codes),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4010)
