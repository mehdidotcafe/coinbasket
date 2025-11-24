# Deployment Guide

## Production Configuration

1. **Environment files**
   - `data_agent/.env.production`: configure public Qdrant endpoint, agent key, OpenAI embedding credentials, and HTTP port bindings.
   - `invest_agent/.env.production`: provide BNB RPC URL/private key, ZeroX API key, Temporal host/port, Postgres connection, agent key, and LangChain thread id.
   - Create `.env.production` by copying `.env.example` and filling secrets before running Nx commands. Keep `.env.production` aligned with hosting secrets (Kubernetes, VM, etc.).

2. **Migrations & infrastructure**
   - Data agent relies solely on Qdrant; ensure the target cluster is available (local Docker via Nx or managed cloud).
   - Invest agent needs Postgres, Temporal, and optionally Redoc. Nx orchestration spins up containers for all dependencies.

## Nx Production Commands

| Task | Command | Description |
| --- | --- | --- |
| Start data agent stack | `./nx infra:production data_agent` | Launches Qdrant (and supporting services) using `docker-compose-production.yml`.
| Run data agent | `./nx start data_agent` | Boots the uAgents service in production mode after infra is ready. |
| Start invest agent infra | `./nx infra:production invest_agent` | Brings up Anvil/Redoc/Postgres (production variants) defined in `invest_agent/docker-compose-production.yml`. |
| Run migrations | `./nx migration:production:run invest_agent` | Applies Alembic migrations against the production Postgres instance. |
| Run invest agent | `./nx start invest_agent` | Starts the investment agent HTTP server in production mode. |
| Start Temporal worker | `./nx start:worker invest_agent` | Spawns the worker that executes on-chain orders via Temporal. |
| Full stack | `./nx start:all` | Convenience command to boot both agents and worker with production settings. |

> ⚠️ **Important:** The worker must be running (`./nx start:worker invest_agent`) for orders to transition from `PENDING` to completed state.

## Docker Compose Files

Each agent contains Docker Compose definitions for local, test, and production scenarios:

- `data_agent/docker-compose.yml`: Development stack bootstrapping Qdrant + agent.
- `data_agent/docker-compose-production.yml`: Production-ready composition (Qdrant + agent) used by Nx infra commands.
- `data_agent/docker-compose-test.yml`: Ephemeral test environment consumed by `./nx test:integration data_agent`.
- `invest_agent/docker-compose.yml`: Development containers (Anvil chain, Redoc, Postgres, agent).
- `invest_agent/docker-compose-production.yml`: Production container layout; pairs with `infra:production` and `start` commands.
- `invest_agent/docker-compose-test.yml`: Ephemeral integration test stack invoked by Nx.

If deploying outside Docker Compose (e.g., Kubernetes), translate these service definitions and environment variables to the target platform.

## Database & Schema Management

- Alembic migration scripts live under `invest_agent/alembic/versions/` and run automatically through Nx migration targets.
- Temporal state references the same PostgreSQL configuration. Ensure credentials have rights to create schemas and run migrations.
- Clean shutdown of dev/test infrastructure uses `./nx infra:test:down <project>` or `./nx infra:down <project>`.

## Continuous Integration

- `.github/workflows/pr-checks.yml` mirrors production setup by installing Node 20, Python 3.13, and running `npx nx lint`, `npx nx test`, and `./nx test:integration` for affected projects. Secrets populate temporary `.env` files to satisfy runtime dependencies.
- `.github/workflows/codeql.yml` provides ongoing static analysis (Actions + Python) on pushes, pull requests, and weekly cron.

## Operational Considerations

- **Agent accessibility:** Ensure that invest agent’s HTTP endpoint is reachable from clients (e.g., `https://app.coinbasket.ai`). Configure reverse proxies or load balancers to route traffic to the running container.
- **Secrets management:** Keep `.env.production` values in a secure secret store (GitHub Actions secrets, Vault, AWS Secrets Manager). Avoid committing sensitive data.
- **Scaling:** For horizontal scaling, run multiple invest agent instances with a shared Postgres/Temporal/Qdrant backend. Ensure unique agent seeds per instance or coordinate conversation threads accordingly.
- **Monitoring:** Leverage Temporal’s UI for workflow visibility and Qdrant’s metrics for vector performance. Consider enabling health checks against `/health` for uptime monitoring.
