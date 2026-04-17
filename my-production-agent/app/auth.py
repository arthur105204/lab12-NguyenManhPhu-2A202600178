from secrets import compare_digest

from fastapi import Header, HTTPException

from app.config import settings


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> str:
    if not x_api_key or not compare_digest(x_api_key, settings.agent_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # In real systems, user identity should come from token/JWT claims.
    return (x_user_id or "user-anonymous").strip()
