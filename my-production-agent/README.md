# My Production Agent (Part 6)

Project này được tạo theo Part 6 trong CODE_LAB.md.

## 1) Setup

```powershell
cd my-production-agent
Copy-Item .env.example .env
```

Chỉnh `AGENT_API_KEY` trong `.env`.

## 2) Run local (Docker Compose)

```powershell
docker compose up --build --scale agent=3
```

## 3) Test

```powershell
curl.exe -i "http://localhost/health"
curl.exe -i "http://localhost/ready"
```

```powershell
$body = '{"question":"Hello"}'
# No key -> 401
curl.exe -i -X POST "http://localhost/ask" -H "Content-Type: application/json" --data-raw $body

# With key -> 200
curl.exe -i -X POST "http://localhost/ask" -H "X-API-Key: change-me-in-production" -H "X-User-Id: user1" -H "Content-Type: application/json" --data-raw $body
```

## 4) Deploy Railway

```powershell
railway init
railway variables set REDIS_URL=redis://<your-redis-host>:6379/0
railway variables set AGENT_API_KEY=<your-secret>
railway up
railway domain
```

## Features covered
- REST API `/ask`
- Conversation history in Redis (stateless)
- Optional streaming endpoint `/ask/stream`
- Multi-stage Docker build
- Env-based config
- API key auth
- Rate limiting (10 req/min)
- Cost guard ($10/month)
- Health `/health` and readiness `/ready`
- Graceful shutdown handling
- Structured JSON logging
