import time

import redis
from fastapi import HTTPException

from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def check_rate_limit(user_id: str):
    now_ms = int(time.time() * 1000)
    window_ms = 60_000

    key = f"rate:{user_id}"
    member = f"{now_ms}-{time.perf_counter_ns()}"

    pipeline = redis_client.pipeline()
    pipeline.zremrangebyscore(key, 0, now_ms - window_ms)
    pipeline.zadd(key, {member: now_ms})
    pipeline.zcard(key)
    pipeline.expire(key, 120)
    _, _, count, _ = pipeline.execute()

    if count > settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": "60"},
        )
