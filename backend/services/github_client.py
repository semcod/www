"""GitHub API client with JWT authentication."""

import time
from pathlib import Path
from typing import Optional

import httpx
import jwt

from config import GITHUB_APP_ID, GITHUB_PRIVATE_KEY_PATH


async def get_installation_token(installation_id: int) -> Optional[str]:
    """Get GitHub App installation access token using JWT."""
    try:
        private_key = Path(GITHUB_PRIVATE_KEY_PATH).read_text()
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + 600,
            "iss": GITHUB_APP_ID,
        }
        encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {encoded_jwt}",
                    "Accept": "application/vnd.github+json",
                },
            )
            data = resp.json()
            return data.get("token")
    except Exception as e:
        print(f"[auth] Token error: {e}")
        return None
