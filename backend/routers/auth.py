import httpx
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import APP_URL, FRONTEND_URL, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_OAUTH_SCOPE, SECRET_KEY, SESSION_EXPIRE_HOURS, REPOS_PER_PAGE, GITHUB_OAUTH_AUTHORIZE_URL, GITHUB_OAUTH_TOKEN_URL, GITHUB_API_BASE_URL, GITEA_CLIENT_ID, GITEA_CLIENT_SECRET, GITEA_OAUTH_AUTHORIZE_URL, GITEA_OAUTH_TOKEN_URL, GITEA_API_BASE_URL
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
    scope = GITHUB_OAUTH_SCOPE
    url = (
        f"{GITHUB_OAUTH_AUTHORIZE_URL}"
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
            GITHUB_OAUTH_TOKEN_URL,
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
            f"{GITHUB_API_BASE_URL}/user",
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




@router.get("/auth/gitea")
async def gitea_oauth_start():
    """Step 1: Redirect user to Gitea OAuth."""
    if not GITEA_CLIENT_ID or not GITEA_OAUTH_AUTHORIZE_URL:
        raise HTTPException(501, "Gitea OAuth not configured")
    from urllib.parse import urlencode
    params = urlencode({
        "client_id": GITEA_CLIENT_ID,
        "redirect_uri": f"{APP_URL}/auth/callback/gitea",
        "response_type": "code",
        "scope": "repo",
    })
    return RedirectResponse(f"{GITEA_OAUTH_AUTHORIZE_URL}?{params}")


@router.get("/auth/callback/gitea")
async def gitea_oauth_callback(code: str):
    """Step 2: Exchange code for token, fetch profile, create user, issue JWT."""
    if not GITEA_CLIENT_ID or not GITEA_OAUTH_TOKEN_URL:
        raise HTTPException(501, "Gitea OAuth not configured")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GITEA_OAUTH_TOKEN_URL,
            json={
                "client_id": GITEA_CLIENT_ID,
                "client_secret": GITEA_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{APP_URL}/auth/callback/gitea",
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_resp.json()

    gitea_token = token_data.get("access_token")
    if not gitea_token:
        raise HTTPException(400, "Gitea OAuth failed")

    async with httpx.AsyncClient() as client:
        profile_resp = await client.get(
            f"{GITEA_API_BASE_URL}/api/v1/user",
            headers={"Authorization": f"token {gitea_token}"},
        )
    profile = profile_resp.json()

    gitea_id = profile.get("id")
    if not gitea_id:
        raise HTTPException(400, "Failed to fetch Gitea profile")

    user = upsert_user(
        github_id=gitea_id,
        login=profile.get("login", ""),
        name=profile.get("full_name", "") or profile.get("login", ""),
        avatar_url=profile.get("avatar_url", ""),
        github_token=gitea_token,
    )

    session_token = create_session_token(user["id"])
    return RedirectResponse(f"{FRONTEND_URL}/audit?session={session_token}")


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
    if not user.get('github_token'):
        raise HTTPException(status_code=401, detail="GitHub token required")
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API_BASE_URL}/user/repos",
            params={"sort": "updated", "per_page": REPOS_PER_PAGE, "type": "owner"},
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
