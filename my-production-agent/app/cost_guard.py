from datetime import datetime, timezone

import redis
from fastapi import HTTPException

from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def _budget_key(user_id: str) -> str:
    month_key = datetime.now(timezone.utc).strftime("%Y-%m")
    return f"budget:{user_id}:{month_key}"


def get_spending(user_id: str) -> float:
    current = redis_client.get(_budget_key(user_id))
    return float(current or 0.0)


def check_budget(user_id: str):
    if get_spending(user_id) >= settings.monthly_budget_usd:
        raise HTTPException(status_code=402, detail="Monthly budget exceeded")


def record_spending(user_id: str, estimated_cost: float):
    if estimated_cost <= 0:
        return

    key = _budget_key(user_id)
    current = redis_client.incrbyfloat(key, estimated_cost)
    redis_client.expire(key, 32 * 24 * 3600)

    if current > settings.monthly_budget_usd:
        raise HTTPException(status_code=402, detail="Monthly budget exceeded")
