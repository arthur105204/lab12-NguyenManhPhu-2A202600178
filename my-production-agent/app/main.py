import json
import logging
import signal
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import redis
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import check_budget, record_spending
from app.rate_limiter import check_rate_limit
from utils.mock_llm import ask, ask_stream


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(payload)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("agent")
logger.handlers.clear()
logger.addHandler(handler)
logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

redis_client = redis.from_url(settings.redis_url, decode_responses=True)
start_time = time.time()
is_ready = False
accepting_requests = True


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class AskResponse(BaseModel):
    user_id: str
    question: str
    answer: str
    history_items: int
    model: str
    timestamp: str


def estimate_cost(question: str, answer: str) -> float:
    token_estimate = len(question.split()) * 2 + len(answer.split()) * 2
    return (token_estimate / 1000.0) * 0.001


@asynccontextmanager
async def lifespan(app: FastAPI):
    global is_ready
    logger.info("startup")
    redis_client.ping()
    is_ready = True
    yield
    is_ready = False
    logger.info("shutdown")


def handle_sigterm(_signum, _frame):
    global accepting_requests
    accepting_requests = False
    logger.info("sigterm_received")


signal.signal(signal.SIGTERM, handle_sigterm)

app = FastAPI(title="My Production Agent", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"

    logger.info(
        json.dumps(
            {
                "event": "request",
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((time.time() - start) * 1000, 1),
            }
        )
    )
    return response


@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - start_time, 1),
        "service": settings.app_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready")
def ready():
    if not is_ready:
        raise HTTPException(status_code=503, detail="not ready")
    try:
        redis_client.ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="redis unavailable") from exc
    return {"ready": True}


@app.post("/ask", response_model=AskResponse)
def ask_agent(
    body: AskRequest,
    user_id: str = Depends(verify_api_key),
):
    if not accepting_requests:
        raise HTTPException(status_code=503, detail="shutting down")

    check_rate_limit(user_id)
    check_budget(user_id)

    history_key = f"history:{user_id}"
    history = [json.loads(item) for item in redis_client.lrange(history_key, 0, -1)]

    answer = ask(body.question)

    now = datetime.now(timezone.utc).isoformat()
    redis_client.rpush(history_key, json.dumps({"role": "user", "content": body.question, "ts": now}))
    redis_client.rpush(history_key, json.dumps({"role": "assistant", "content": answer, "ts": now}))
    redis_client.ltrim(history_key, -settings.history_max_items, -1)

    record_spending(user_id, estimate_cost(body.question, answer))

    return AskResponse(
        user_id=user_id,
        question=body.question,
        answer=answer,
        history_items=len(history) + 2,
        model=settings.llm_model,
        timestamp=now,
    )


@app.post("/ask/stream")
def ask_agent_stream(
    body: AskRequest,
    user_id: str = Depends(verify_api_key),
):
    check_rate_limit(user_id)
    check_budget(user_id)

    def token_stream():
        for token in ask_stream(body.question):
            yield token

    return StreamingResponse(token_stream(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port)
