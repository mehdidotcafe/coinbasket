# Development Guide

## Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| Node.js | ≥ 22.0.0 | Required for Nx command runner and shared tooling. |
| Python | ≥ 3.10 (< 4.0) | Each agent managed via Poetry; Nx commands install the virtualenv automatically. |
| Docker & Docker Compose | Latest stable | Needed for local Qdrant, Anvil (BNB chain clone), Postgres, Redoc containers. |
| Poetry | Installed automatically by Nx/CI | Used behind the scenes by Nx `install` tasks. |

Install Node dependencies once from the repository root:

```bash
npm install
```

## Environment Configuration

Each agent ships example environment files:

- Duplicate `data_agent/.env.example` to `.env.local` (development) or `.env.production` (production) and provide API keys (OpenAI embeddings, Qdrant) plus agent credentials.
- Duplicate `invest_agent/.env.example` to `.env.local` or `.env.production` to configure BNB RPC endpoints, ZeroX keys, Temporal host, Postgres credentials, and agent keys.

During CI the PR workflow writes a temporary `.env` from GitHub secrets before running tests. Replicate locally with:

```bash
cp data_agent/.env.example data_agent/.env.test
cp invest_agent/.env.example invest_agent/.env.test
# Populate secrets as needed
```

## Installing Python Dependencies

Nx wraps Poetry so per-project dependencies install via:

```bash
./nx install data_agent
./nx install invest_agent
```

This generates `.venv/` folders inside each agent package. Run `npm install` first so Nx is available.

## Local Development Commands

| Goal | Command | Description |
| --- | --- | --- |
| Run data agent in dev mode | `./nx dev data_agent` | Starts Qdrant container and the uAgents HTTP server with live ingestion of tokens/baskets. |
| Run invest agent in dev mode | `./nx dev invest_agent` | Boots Anvil chain, Redoc docs, Postgres, then launches the agent. |
| Start Temporal worker | `./nx dev:worker invest_agent` | Processes asynchronous investment orders; required for order execution in dev. |
| Run full stack (data + invest + worker) | `./nx dev:all` | Convenience task that orchestrates all dev services. |
| Tear down dev infrastructure | `./nx infra:down data_agent` / `./nx infra:down invest_agent` | Stops Docker services for the target agent. |

### Integration-Test Stack

`script/run_integration_tests.sh` coordinates Nx infra commands, spawns agent processes with `.env.test`, waits for readiness, and invokes Pytest markers `-k test_integration`. The helper is executed by:

```bash
./nx test:integration data_agent
./nx test:integration invest_agent
```

For the invest agent, the script also launches the worker in the background so Temporal workflows can submit on-chain transactions.

## Linting & Testing

| Type | Command | Notes |
| --- | --- | --- |
| Lint | `npx nx lint <project>` | Runs Ruff/ESLint pipelines defined per project. |
| Unit tests | `npx nx test <project>` | Uses Pytest with coverage settings defined in each `pyproject.toml`. |
| Integration tests | `./nx test:integration <project>` | Wraps the integration script described above. |

CI mirrors these exact commands in `.github/workflows/pr-checks.yml`, automatically detecting affected projects with `npx nx show projects --affected` and running lint/unit/integration jobs with generated `.env` files.

## Useful Utilities

- `script/wait_agent_start.sh`: Polls agent endpoints until healthy; used by integration workflow.
- `nx project.json` & `nx.json`: Define the Nx targets referenced above (install, dev, start, infra, migration, test).
- `reports/` & `coverage/`: Nx tasks output HTML/coverage artefacts per agent.

## Troubleshooting Tips

- If Nx reports missing virtualenvs, re-run `./nx install <project>` after deleting `.venv/`.
- Ensure Docker Desktop or daemon is running before invoking `./nx dev ...`; startup assumes Docker Compose is available.
- When tweaking `.env` values, restart the Nx dev process so uAgents re-read credentials.
