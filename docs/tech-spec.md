# coinbasket - Technical Specification

**Author:** coinbasket
**Date:** 2025-11-23
**Project Level:** Quick Flow (Brownfield)
**Change Type:** TBD — capture in Step 2 discovery
**Development Context:** Brownfield Nx-managed Python agent monorepo (data_agent, invest_agent, protocol, shared)

---

## Context

### Available Documents
- docs/document-project/project-scan.md — Brownfield project scan summarizing monorepo structure, documentation inventory, tech stack, and integration flows for data_agent, invest_agent, protocol, and shared packages.
- No product brief (`docs/*brief*.md`) or research (`docs/*research*.md`) documents detected via automated search.
- No brownfield index (`docs/index.md`) present; project-scan.md is the authoritative map for existing context today.

### Project Stack
- Monorepo orchestration via Nx 20.8.1 with @nxlv/python executors; Node.js tooling kept minimal (root `package.json` only brings Nx + env-cmd).
- All services target Python 3.10 with Poetry 2.1.2 lockfiles and Ruff for linting; pytest drives unit suites with asyncio support and coverage fan-out into `coverage/<service>/`.
- `data_agent` runtime: uAgents 0.22.4, LangChain 0.3.25 (+ OpenAI extras), LangChain-Qdrant 0.2.0, Qdrant Client 1.14.2, async ingestion pipelines populating vector search collections.
- `invest_agent` runtime: uAgents 0.22.4, LangGraph 1.0.1, LangChain-Core 1.0.1, LangChain-OpenAI 1.0.1, TemporalIO 1.18.1, Web3.py 7.10.0, SQLAlchemy 2.0.x, AsyncPG 0.30.0, Alembic migrations, LangGraph SQLite checkpoints.
- `protocol` package supplies shared domain models on Python 3.10 with uAgents 0.22.3; `shared` package centralizes HTTP (aiohttp 3.12.13, requests 2.32.4) and utility helpers on top of Pydantic 2.11.7.
- Infrastructure: docker-compose definitions per agent (dev/test/prod), env-cmd-managed environment switching, Nx targets for infra spin-up (`nx run <agent>:infra`) and Alembic migrations.

### Existing Codebase Structure
- Monorepo layout mirrors Nx project roots: `data_agent/`, `invest_agent/`, `protocol/`, `shared/`, each with dedicated Poetry environment, coverage reports, and Nx targets. Shared docs live under `docs/document-project/` for brownfield mapping.
- Each agent keeps domain-focused packages (e.g., `invest_agent/invest_agent/asset`, `conversation`, `investment`, `portfolio`, `infrastructure`); entry points in `main.py`, `worker.py`, and CLI modules manage uAgents orchestration, LangGraph flows, Temporal workers, and HTTP endpoints.
- `data_agent` bootstraps ingestion pipelines from curated datasets and PancakeSwap listings into Qdrant collections; exposes REST handlers aligned with protocol fixtures (`protocol.fixture`).
- `protocol` provides typed message schemas and fixtures; `shared` centralizes HTTP clients, ID generators, randomization utilities—consumed as editable Poetry dependencies by both agents.
- Testing conventions: tests colocated under `*/test/` with `*_test.py` naming, `pytest.ini` enabling async mode, coverage reports routed per service, and integration tests staged under `invest_agent/invest_agent/integration_test` with supporting database fixture scripts.

---

## The Change

### Problem Statement

_To be captured in Step 2._

### Proposed Solution

_To be captured in Step 2._

### Scope

**In Scope:**

_To be captured in Step 2._

**Out of Scope:**

_To be captured in Step 2._

---

## Implementation Details

### Source Tree Changes

_Pending Step 3 outputs._

### Technical Approach

_Pending Step 3 outputs._

### Existing Patterns to Follow

_Pending Step 3 outputs._

### Integration Points

_Pending Step 3 outputs._

---

## Development Context

### Relevant Existing Code

_Pending Step 3 outputs._

### Dependencies

**Framework/Libraries:**

_Pending Step 3 outputs._

**Internal Modules:**

_Pending Step 3 outputs._

### Configuration Changes

_Pending Step 3 outputs._

### Existing Conventions (Brownfield)

_Pending confirmation._

### Test Framework & Standards

_Pending Step 3 outputs._

---

## Implementation Stack

_Pending Step 3 outputs._

---

## Technical Details

_Pending Step 3 outputs._

---

## Development Setup

_Pending Step 3 outputs._

---

## Implementation Guide

### Setup Steps

_Pending Step 3 outputs._

### Implementation Steps

_Pending Step 3 outputs._

### Testing Strategy

_Pending Step 3 outputs._

### Acceptance Criteria

_Pending Step 3 outputs._

---

## Developer Resources

### File Paths Reference

_Pending Step 3 outputs._

### Key Code Locations

_Pending Step 3 outputs._

### Testing Locations

_Pending Step 3 outputs._

### Documentation to Update

_Pending Step 3 outputs._

---

## UX/UI Considerations

_Pending Step 3 outputs._

---

## Testing Approach

_Pending Step 3 outputs._

---

## Deployment Strategy

### Deployment Steps

_Pending Step 3 outputs._

### Rollback Plan

_Pending Step 3 outputs._

### Monitoring

_Pending Step 3 outputs._
