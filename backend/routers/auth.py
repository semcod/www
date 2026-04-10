import httpx
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import APP_URL, FRONTEND_URL, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, SECRET_KEY, SESSION_EXPIRE_HOURS, DEMO_MODE
from database import upsert_user, get_user_by_id

router = APIRouter()
security = HTTPBearer(auto_error=False)


def create_session_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=SESSION_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_session_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if not credentials:
        raise HTTPException(401, "Not authenticated")
    payload = decode_session_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid token payload")
    user = get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(401, "User not found")
    return user


@router.get("/auth/github")
async def github_oauth_start():
    """Step 1: Redirect user to GitHub OAuth."""
    scope = "repo,read:org"
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope={scope}"
        f"&redirect_uri={APP_URL}/auth/callback"
    )
    return RedirectResponse(url)


@router.get("/auth/callback")
async def github_oauth_callback(code: str):
    """Step 2: Exchange code for token, fetch profile, create user, issue JWT."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_resp.json()

    github_token = token_data.get("access_token")
    if not github_token:
        raise HTTPException(400, "OAuth failed")

    async with httpx.AsyncClient() as client:
        profile_resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
            },
        )
    profile = profile_resp.json()

    github_id = profile.get("id")
    if not github_id:
        raise HTTPException(400, "Failed to fetch GitHub profile")

    user = upsert_user(
        github_id=github_id,
        login=profile.get("login", ""),
        name=profile.get("name", "") or profile.get("login", ""),
        avatar_url=profile.get("avatar_url", ""),
        github_token=github_token,
    )

    session_token = create_session_token(user["id"])
    return RedirectResponse(f"{FRONTEND_URL}/audit?session={session_token}")


@router.post("/auth/demo")
async def demo_login():
    """Demo login: create a demo user and return JWT session token.
    Only available when DEMO_MODE=1 is set.
    """
    if not DEMO_MODE:
        raise HTTPException(403, "Demo mode not enabled")

    user = upsert_user(
        github_id=0,
        login="demo-user",
        name="Demo User",
        avatar_url="https://avatars.githubusercontent.com/u/0?v=4",
        github_token="",
    )
    session_token = create_session_token(user["id"])
    return {"session": session_token, "user": {"login": user["login"], "name": user["name"], "avatar_url": user["avatar_url"]}}


@router.get("/api/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "login": user["login"],
        "name": user["name"],
        "avatar_url": user["avatar_url"],
    }


@router.post("/api/logout")
async def logout():
    return {"message": "Logged out"}


@router.get("/api/repos")
async def list_repos(user: dict = Depends(get_current_user)):
    """List user's repos for audit selection."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.github.com/user/repos",
            params={"sort": "updated", "per_page": 30, "type": "owner"},
            headers={
                "Authorization": f"Bearer {user['github_token']}",
                "Accept": "application/vnd.github+json",
            },
        )
    repos = resp.json()
    return [
        {
            "full_name": r["full_name"],
            "name": r["name"],
            "language": r.get("language"),
            "stars": r.get("stargazers_count", 0),
            "size_kb": r.get("size", 0),
            "private": r.get("private", False),
            "default_branch": r.get("default_branch", "main"),
        }
        for r in repos
        if isinstance(r, dict)
    ]
