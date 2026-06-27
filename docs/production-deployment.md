# Production Deployment

MultiShield AI is deployed as a containerized stack with five runtime layers:

1. Nginx as the public reverse proxy.
2. Frontend served as static assets from a container.
3. FastAPI backend.
4. PostgreSQL for durable analysis and workflow data.
5. Redis for background queueing and future async work.

## Runtime Topology

- Public traffic enters Nginx on port 80.
- Browser requests for `/` are routed to the frontend container.
- API calls are routed through `/api/*` to the backend service.
- The backend exposes `/health`, `/ready`, and `/metrics`.
- Prometheus scrapes backend metrics and Grafana visualizes them.

## Environment Variables

Use `.env.example` as the starting point for production secrets and connection strings.

Required values:

- `DATABASE_URL`
- `REDIS_URL`
- `POSTGRES_PASSWORD`
- `GRAFANA_ADMIN_PASSWORD`

Recommended values:

- `APP_ENV=production`
- `DEBUG=false`
- `ENABLE_DOCS=false`
- `LOG_LEVEL=INFO`

## EC2 Flow

1. Provision an EC2 instance with at least 2 vCPU and 4 GB RAM.
2. Install Docker using `scripts/bootstrap-ec2.sh`.
3. Clone this repository into `/opt/multishield-ai`.
4. Copy `.env.example` to `.env` and fill in production values.
5. Start the stack with `docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d --build`.

## Validation Endpoints

- `GET /health` for liveness.
- `GET /ready` for readiness.
- `GET /metrics` for Prometheus scraping.