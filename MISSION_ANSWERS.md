# Day 12 Lab - Mission Answers

## Student Info
- Name: [Your Name]
- Student ID: [Your Student ID]
- Date: 2026-04-17

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcoded secrets in source code.
2. Fixed host/port and debug-style configuration.
3. No robust health and readiness workflow for orchestrators.
4. Logging not structured and can leak sensitive information.
5. Missing graceful shutdown behavior in basic implementation.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---|---|---|---|
| Config | Hardcoded values | Environment variables | Safe secret handling and portability |
| Health checks | Minimal/absent | Dedicated health and readiness endpoints | Enables restart and traffic control |
| Logging | Print-style | Structured JSON logging | Better observability and incident response |
| Shutdown | Abrupt stop | Graceful shutdown with signal handling | Prevents request/data loss |
| Security | Weak/no auth guard | API key auth, rate limit, budget guard | Prevents abuse and cost overrun |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: python:3.11 in develop, python:3.11-slim in production runtime.
2. Working directory: /app.
3. COPY requirements first to maximize Docker layer cache.
4. CMD sets default run command; ENTRYPOINT defines main executable behavior and is stricter to override.

### Exercise 2.3: Image size comparison
- Develop image: 1.15 GB (my-agent:develop)
- Production image: 160 MB (my-agent:advanced)
- Difference: about 86.1 percent smaller in production image

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://alluring-enjoyment-production-4b1d.up.railway.app
- Platform: Railway
- Result: deployment success on service alluring-enjoyment
- Verified:
  - GET /health returns 200
  - GET /ready returns 200
  - POST /ask without key returns 401
  - POST /ask with valid key returns 200

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- Auth test: 401 without X-API-Key, 200 with valid key
- Rate limit test (10 req/min): first 10 requests returned 200, request 11 returned 429
- JSON request validation works on cloud endpoint with application/json payload

### Exercise 4.4: Cost guard implementation
- Budget is tracked per user and per month in Redis.
- Budget key format: budget:user_id:YYYY-MM.
- API blocks with 402 when monthly budget is exceeded.

## Part 5: Scaling and Reliability

### Exercise 5.1-5.5 implementation notes
- Health endpoint implemented.
- Readiness endpoint implemented with Redis check.
- Graceful shutdown signal handling implemented.
- Stateless design implemented by moving user history, rate window, and budget tracking to Redis.
- Load balancer layer implemented via Nginx in Docker Compose.
- Conversation history persists for same user across multiple requests.

## Part 6: Final Project summary
- Built project from scratch at folder my-production-agent following Part 6 steps.
- Included modules:
  - app/config.py
  - app/auth.py
  - app/rate_limiter.py
  - app/cost_guard.py
  - app/main.py
- Included infra files:
  - Dockerfile (multi-stage)
  - docker-compose.yml (agent + redis + nginx)
  - .env.example, .dockerignore, requirements.txt, railway.toml

## Validation evidence
- Local end-to-end tests passed (health, ready, auth, history, stream, rate limit).
- Cloud end-to-end tests passed on Railway public URL with required status codes.
