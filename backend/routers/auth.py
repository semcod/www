import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from config import APP_URL, FRONTEND_URL, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

router = APIRouter()


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
    """Step 2: Exchange code for token, redirect to frontend."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        data = resp.json()

    token = data.get("access_token")
    if not token:
        raise HTTPException(400, "OAuth failed")

    return RedirectResponse(f"{FRONTEND_URL}/audit?token={token}")


@router.get("/api/repos")
async def list_repos(token: str):
    """List user's repos for audit selection."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.github.com/user/repos",
            params={"sort": "updated", "per_page": 30, "type": "owner"},
            headers={
                "Authorization": f"Bearer {token}",
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
