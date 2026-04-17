# Deployment Information

## Public URL
https://alluring-enjoyment-production-4b1d.up.railway.app

## Platform
Railway

## Project and Service
- Project: alluring-enjoyment
- Environment: production
- App service: alluring-enjoyment
- Redis service: Redis

## Variables configured (app service)
- AGENT_API_KEY
- REDIS_URL
- LOG_LEVEL
- RATE_LIMIT_PER_MINUTE
- MONTHLY_BUDGET_USD

## Cloud test commands used

### Health
curl.exe -i "https://alluring-enjoyment-production-4b1d.up.railway.app/health"

### Readiness
curl.exe -i "https://alluring-enjoyment-production-4b1d.up.railway.app/ready"

### Ask without key (expected 401)
curl.exe -i -X POST "https://alluring-enjoyment-production-4b1d.up.railway.app/ask" -H "Content-Type: application/json" --data-raw '{"question":"Hello"}'

### Ask with key (expected 200)
curl.exe -i -X POST "https://alluring-enjoyment-production-4b1d.up.railway.app/ask" -H "X-API-Key: part6-secret-key" -H "X-User-Id: cloud-user" -H "Content-Type: application/json" --data-raw '{"question":"Hello"}'

## Cloud verification results
- health=200
- ready=200
- ask_without_key=401
- ask_with_key=200
- rate_limit sequence=200,200,200,200,200,200,200,200,200,200,429
- history_items_first=2
- history_items_second=4

## Source folder deployed
- my-production-agent

## Notes
- Deployment used railway up with path-as-root to deploy only the my-production-agent folder.
- App uses Redis for history, rate limiting, and budget tracking to satisfy stateless requirement.
