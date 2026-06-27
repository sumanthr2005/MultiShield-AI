# Customer Deployment Guide

## What You Deploy

The customer deployment includes:

- Frontend user interface.
- Backend inference and workflow API.
- PostgreSQL database.
- Redis queue.
- Nginx reverse proxy.
- Prometheus and Grafana for monitoring.

## Prerequisites

- Linux host or EC2 instance.
- Docker Engine and Docker Compose plugin.
- DNS record pointing to the EC2 public IP.
- TLS certificate in front of Nginx, or an external load balancer terminating TLS.

## Installation Steps

1. Copy `.env.example` to `.env`.
2. Set strong secrets for Postgres and Grafana.
3. Update `CORS_ORIGINS` to the customer domain.
4. Run `docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d --build`.
5. Confirm `http://<host>/health` returns `ok`.

## Operational Checks

- Check application readiness with `GET /ready`.
- Check Prometheus at `http://<host>:9090`.
- Check Grafana at `http://<host>:3000`.
- Review container logs with `docker compose logs -f`.

## Upgrade Procedure

1. Pull the latest repository changes.
2. Review `.env` for new variables.
3. Run `./scripts/deploy.sh` on the EC2 host.
4. Verify the health and readiness endpoints after rollout.