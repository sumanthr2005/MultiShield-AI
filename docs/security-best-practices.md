# Security Best Practices

## Secrets

- Never commit `.env`.
- Rotate `POSTGRES_PASSWORD`, `GRAFANA_ADMIN_PASSWORD`, and SSH keys regularly.
- Store sensitive values in a secret manager when moving beyond a pilot deployment.

## Network Controls

- Expose only Nginx publicly.
- Keep PostgreSQL and Redis on private networks only.
- Restrict EC2 security group ingress to the customer IP ranges where possible.

## Application Controls

- Leave `ENABLE_DOCS=false` in production unless API documentation is intentionally public.
- Use strong CORS allow lists instead of `*` in production.
- Keep the backend stateless and store durable data in PostgreSQL.

## Container Hygiene

- Rebuild images from source on every release.
- Run containers with restart policies and minimal privileges.
- Keep base images pinned to known versions.

## Transport Security

- Terminate TLS before Nginx or at Nginx itself.
- Redirect HTTP to HTTPS.
- Use HSTS after validating the deployment path.