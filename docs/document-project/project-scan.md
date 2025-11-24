# Project Scan Notes

## Step 1 – Project Structure Classification

- Repository type: monorepo spanning coordinated Python services with shared libraries.
- Detected parts and inferred project types:

| Part | Path | Detected Type | Key Signals |
| --- | --- | --- | --- |
| data_agent | data_agent/ | data platform | `pyproject.toml` with LangChain/Qdrant stack, uAgents configuration, ingestion pipelines |
| invest_agent | invest_agent/ | backend service | `pyproject.toml` with Web3, LangGraph, Temporal, Postgres connectors, conversational tooling |
| protocol | protocol/ | shared protocol library | Lightweight uAgents protocol package consumed by agents |
| shared | shared/ | utility library | Reusable HTTP, ID, randomness helpers shared across agents |

## Step 2 – Existing Documentation & User Context

### Documentation Inventory

| File | Focus | Notes |
| --- | --- | --- |
| README.md | Monorepo overview | Landing documentation at repository root |
| data_agent/README.md | Data ingestion & similarity agent | Describes data sources and agent responsibilities |
| invest_agent/README.md | Investment execution agent | Covers workflow, endpoints, and orchestration details |
| protocol/README.md | Shared protocol models | Documents domain contracts exchanged between agents |
| shared/README.md | Utility library | Explains shared helpers leveraged by other packages |
| docs/sprint-artifacts/ | Sprint artifacts folder | Present but currently empty |

### Additional Context From User

| Source | Description |
| --- | --- |
| attachement/Untitled 1cf23f03ab1a8086aca2edbb6278a9c2.csv | Board snapshot highlighting Done → Draft work items across product and platform streams |
| attachement/Untitled 1cf23f03ab1a8086aca2edbb6278a9c2_all.csv | Full Kanban export including TODO/Ready/In progress/Blocked items with story tags |

User confirmed these exports should inform prioritization and documentation focus.

## Step 3 – Technology Stack & Architecture Patterns

### Technology Stack Summary

| Part | Category | Technology | Notes |
| --- | --- | --- | --- |
| data_agent | Language & Runtime | Python 3.10 (Poetry managed) | Async uAgents runtime hosted locally |
|  | AI/Vector | LangChain, LangChain-Qdrant, OpenAI Embeddings | Embeddings persisted to Qdrant for similarity search |
|  | Storage | Qdrant vector store | Managed via `QdrantClient` with collection settings from config |
|  | Integrations | PancakeSwap token list, curated basket data sources | Ingestion pipelines populate vector index at startup |
|  | HTTP/Agent | uAgents REST + message handlers | Exposes `/`, `/basket`, `/asset` endpoints with agent-key auth |
| invest_agent | Language & Runtime | Python 3.10 (Poetry) | Async uAgents agent hosting LangGraph workflows |
|  | AI Orchestration | LangChain, LangGraph, LangGraph SQLite checkpoints | create_react_agent drives conversational tooling |
|  | Blockchain | Web3.py (Async), BSC chain wrappers, ZeroX API | Temporal-backed order submitter orchestrates swaps |
|  | Persistence | Postgres via SQLAlchemy, LangChain SQLite cache | Repository layer separated via SQLAlchemy session manager |
|  | Workflow | Temporal, AioHTTP agent-to-agent client | Temporal order worker + cross-agent calls to data_agent |
| protocol | Language | Python 3.10 | Defines shared domain models used by both agents |
|  | Agent Messaging | uAgents | Ensures consistent serialization across agent boundary |
| shared | Language | Python 3.10 | Centralized utilities (HTTP clients, ID/random generators) |
|  | Networking | aiohttp, requests | Provides sync/async HTTP abstractions reusable in agents |

### Architecture Patterns Observed

- data_agent operates as an ingestion-first microservice: on startup it hydrates Qdrant using curated data sources, then offers similarity and basket retrieval endpoints secured by agent keys.
- invest_agent functions as an orchestrated autonomous agent: LangGraph tools call out to data_agent, Temporal handles long-lived order execution, and Web3 interfaces submit transactions to BNB Chain.
- protocol and shared libraries enforce strong contract boundaries, letting domain objects and infrastructure utilities evolve once and propagate to both agents.

## Step 4 – API & Data Model Documentation

### API Contracts

| Part | Output | Highlights |
| --- | --- | --- |
| invest_agent | `docs/document-project/api-contracts-invest_agent.md` | Catalogued `/conversation`, `/conversation/messages`, `/asset/swap/price`, `/portfolio`, `/auth`, `/health`, and `/openapi` endpoints, including authentication behavior and LangGraph/Temporal dependencies. |

### Data Models

| Part | Output | Highlights |
| --- | --- | --- |
| invest_agent | `docs/document-project/data-models-invest_agent.md` | Documented Postgres schema for orders, tries, chain transactions, transactions, and postings, plus serialization patterns and repository usage. |
| data_agent | `docs/document-project/data-models-data_agent.md` | Described Qdrant vector collection (1,536-dim embeddings) and ingestion pipelines sourcing PancakeSwap tokens and curated baskets. |

### Scan Notes

- Exhaustive scan ran against `invest_agent/invest_agent` and related infrastructure modules to map REST contracts and SQLAlchemy models.
- Data agent ingestion modules reviewed to capture vector-store metadata and deterministic ID strategy.
- Outputs saved in `docs/document-project/` and logged in the scan state for resumability.

## Step 6 – Development & Deployment Workflows

### Development Instructions

| Output | Highlights |
| --- | --- |
| `docs/document-project/development-guide.md` | Documents prerequisites (Node≥22, Python≥3.10, Docker), Nx install flow, `.env` setup, dev orchestration commands (`./nx dev`, `./nx dev:all`), and lint/test pipelines (`npx nx lint`, `npx nx test`, `./nx test:integration`). |

### Deployment Configuration

| Output | Highlights |
| --- | --- |
| `docs/document-project/deployment-guide.md` | Explains production `.env` requirements, Nx infra/start/migration commands, Docker Compose usage, GitHub workflows, and operational watchpoints (worker uptime, secrets, monitoring). |

### Additional Notes

- No `CONTRIBUTING.md` found; contribution process pending.
- CI pipeline (`.github/workflows/pr-checks.yml`) mirrors local commands with Nx detection and `.env` secret injection. CodeQL workflow provides weekly scans.

## Step 7 – Integration Architecture

| Output | Highlights |
| --- | --- |
| `docs/document-project/integration-architecture.md` | Maps agent-to-agent flows (HTTP + Fetch.ai), describes protocol/shared dependencies, and traces data paths through Qdrant, Temporal, Postgres, and ZeroX. Notes authentication requirements and future event-driven enhancements. |
