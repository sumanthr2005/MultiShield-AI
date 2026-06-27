# Scaling Recommendations

## Near-Term

- Run the stack on an EC2 instance with enough memory to keep PostgreSQL, Redis, and Grafana stable.
- Keep the backend container stateless so it can be scaled horizontally.
- Put an AWS Application Load Balancer in front of Nginx for TLS termination and basic failover.

## Horizontal Scale

- Increase backend replicas behind the reverse proxy when request volume grows.
- Move PostgreSQL to RDS before the database becomes a bottleneck.
- Move Redis to Elasticache if queue depth or latency rises.

## Capacity Signals

- CPU above 70 percent for sustained periods.
- Memory pressure or OOM kills.
- Rising 95th percentile latency.
- Queue backlog growth in Redis.

## Suggested Sizing Start Point

- Small pilot: 2 vCPU, 4 GB RAM.
- First production rollout: 2-4 vCPU, 8 GB RAM.
- Growth environment: separate instances for app, database, and observability.