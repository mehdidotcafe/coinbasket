# Source Tree Analysis

## Monorepo Layout

```text
coinbasket/
├── data_agent/                     # Part: data_agent – ingestion & similarity service
│   ├── data_agent/
│   │   ├── main.py                 # uAgents entry point; bootstraps ingestion & REST handlers
│   │   ├── configuration.py        # Loads environment-driven agent settings (ports, keys, Qdrant)
│   │   ├── ingestion/              # Pipelines that hydrate Qdrant with token & basket metadata
│   │   │   ├── data_source/        # Abstract + infrastructure implementations (PancakeSwap, curated baskets)
│   │   │   └── id/                 # Deterministic ID generation utilities for vector documents
│   │   ├── similarity/             # Qdrant-backed similarity storage and search use cases
│   │   ├── asset/                  # Use cases for deterministic asset lookups by ID
│   │   └── integration_test/       # Contract-level integration coverage for ingestion/search flows
│   └── pyproject.toml              # Poetry project definition (LangChain, Qdrant, shared libs)
├── invest_agent/                   # Part: invest_agent – autonomous investment & portfolio agent
│   ├── invest_agent/
│   │   ├── main.py                 # uAgents entry point exposing REST + toolchain integration
│   │   ├── registry.py             # Dependency wiring (Web3, ZeroX, Temporal, repositories)
│   │   ├── investment/             # Build/execute investment plans, order lifecycle, ZeroX integration
│   │   │   └── order/              # SQLAlchemy repositories, Temporal submitter, domain order logic
│   │   ├── portfolio/              # Portfolio aggregation, small balance policies, postings queries
│   │   ├── conversation/           # LangGraph agent tooling, threaded conversation persistence
│   │   ├── chain/                  # BNB chain abstractions (nonce manager, transaction parsing, balances)
│   │   ├── documentation/          # OpenAPI descriptions and error payloads
│   │   ├── database/               # SQLAlchemy base classes and session management
│   │   ├── storage/                # Local storage helpers (e.g., LangGraph checkpoints)
│   │   ├── worker.py               # Temporal worker bootstrap for order execution workflows
│   │   └── integration_test/       # Cross-cutting integration tests for APIs and execution flows
│   ├── alembic/                    # Database migrations for orders/transactions/postings schema
│   └── pyproject.toml              # Poetry project definition (Web3, LangGraph, Temporal, Postgres)
├── protocol/                       # Part: protocol – shared domain contracts
│   ├── protocol/
│   │   ├── token.py                # Token domain model used across agents
│   │   ├── basket.py               # Basket aggregate & validation helpers
│   │   └── fixture/                # Prebuilt domain fixtures for testing and tooling
│   └── pyproject.toml              # Lightweight packaging for shared protocol artefacts
├── shared/                         # Part: shared – cross-agent infrastructure utilities
│   ├── shared/
│   │   ├── http_request/           # aiohttp & requests adapters consumed by agents
│   │   ├── id_generator/           # UUID + deterministic ID helper
│   │   └── random_generator/       # Randomness utilities supporting order IDs & seeds
│   └── pyproject.toml              # Poetry project definition for shared helpers
├── docs/                           # Documentation outputs and sprint artefacts
│   ├── document-project/           # Generated modernization documentation set
│   └── sprint-artifacts/           # Placeholder for historical sprint notes (currently empty)
├── assets/                         # Static marketing artefacts (landing page content)
├── script/                         # Helper scripts for integration testing & agent orchestration
├── nx.json / project.json          # Nx monorepo orchestration metadata
└── package.json                    # Root Node ecosystem configuration (frontend assets & tooling)
```

## Critical Folders Summary

| Folder | Part | Purpose |
| --- | --- | --- |
| `data_agent/data_agent/ingestion` | data_agent | Drives ingestion use case; fetches PancakeSwap + curated basket datasets and upserts them into Qdrant. |
| `data_agent/data_agent/similarity` | data_agent | Implements vector search abstractions and similarity use cases exposed via REST and agent messaging. |
| `invest_agent/invest_agent/investment` | invest_agent | Core execution logic: plan construction, pricing, order submission through ZeroX and Temporal workflows. |
| `invest_agent/invest_agent/portfolio` | invest_agent | Aggregates holdings from postings and transactions to answer portfolio queries. |
| `invest_agent/invest_agent/conversation` | invest_agent | LangGraph tooling and conversational state management for the autonomous assistant surface. |
| `invest_agent/alembic` | invest_agent | Database migration history for Postgres schema backing orders, transactions, and postings. |
| `protocol/protocol` | protocol | Shared token/basket contracts and fixtures, ensuring both agents serialize/deserialize identical payloads. |
| `shared/shared/http_request` | shared | Provides sync/async HTTP adapters reused by both agents when calling external services. |
| `script/` | monorepo | Shell scripts that orchestrate integration environments and wait for agents to bootstrap (e.g., CI pipelines). |

## Interface Highlights

- **Agent-to-Agent Calls**: `invest_agent/invest_agent/conversation/tools.py` (through registry wiring) leverages `shared/http_request` clients to talk to data_agent’s similarity endpoints.
- **Shared Domain Models**: Both agents import from `protocol/protocol` to guarantee consistent asset and basket representations.
- **Temporal & Database**: `invest_agent/invest_agent/registry.py` wires Temporal, Postgres, and ZeroX clients together, connecting runtime orchestration with persistence under `invest_agent/alembic` migrations.
