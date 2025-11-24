# Integration Architecture

## Overview

Coinbasket operates as a coordinated multi-agent system with a shared protocol and utility layer:

- **data_agent** – Vector-backed knowledge service that ingests curated baskets and token lists, exposing similarity queries and deterministic asset lookups.
- **invest_agent** – Conversational investment executor which consumes data_agent APIs, manages portfolios, and submits on-chain orders via Temporal + ZeroX.
- **protocol** – Shared domain contracts (`Token`, `Basket`, query/response models) guaranteeing consistent serialization across agents.
- **shared** – Common infrastructure utilities (HTTP clients, ID/random generators) reused by both agents and integration scripts.

## Communication Patterns

| From | To | Type | Interface | Notes |
| --- | --- | --- | --- | --- |
| invest_agent | data_agent | Agent-to-agent (HTTP) | `AiohttpAgentToAgentClient` → `/` (similarity search), `/basket`, `/asset` | LangGraph tools call `agent_to_agent_client.send_and_receive_message`, attaching `agent_key` for auth; responses mapped into protocol models. |
| invest_agent | data_agent | Agent-to-agent (Fetch.ai messaging) | `FetchAiAgentToAgentClient` | Alternative dispatcher using Fetch.ai messaging for non-HTTP channels; same protocol payloads. |
| data_agent | Qdrant | Vector store API | `QdrantLangChainSimilarityStorage` | Ingestion pipelines upsert tokens/baskets; similarity queries fetch top vectors with metadata filters. |
| invest_agent | Postgres | SQL (async) | SQLAlchemy repositories (`orders`, `transactions`, `postings`) | Stores order lifecycle, executed transactions, and postings powering portfolio balances. |
| invest_agent | Temporal | gRPC | `TemporalOrderSubmitter` | Submits asynchronous workflows to execute Binance Chain transactions and handle retries. |
| invest_agent | ZeroX API | HTTPS | `ZeroXApiClient` | Quotes swap prices and executes trades; feeds into order/transaction flows. |
| invest_agent | data_agent | REST `/basket` | `GetAllBasketsQuery` | Used by tools to fetch curated basket catalog for UI and planning. |

## Data Flows

1. **Similarity & Basket Discovery**
   - LangGraph tool `get_tokens_from_query` builds `SimilarAssetsQuery` (TOKEN/BASKET) and calls data_agent via `agent_to_agent_client`.
   - data_agent verifies `agent_key`, executes vector search against Qdrant, and returns `TokenResponse`/`BasketResponse` payloads.
   - invest_agent converts responses back to domain objects and presents them in conversational replies.

2. **Investment Planning & Execution**
   - `BuildPricedInvestmentPlanUseCase` fetches price quotes; `ExecuteInvestmentPlanUseCase` submits orders to Temporal, which interacts with ZeroX + Web3.
   - Completed transactions emit postings that portfolio queries aggregate via SQLAlchemy repositories.

3. **Shared Schema**
   - Both agents import from `protocol/protocol` to ensure identical serialization of tokens and baskets. Tests in `protocol/` guarantee parity.

## Integration Considerations

- **Authentication**: All cross-agent HTTP requests use `agent_key` validation in data_agent’s REST handlers. Keep keys aligned across `.env` files.
- **Resilience**: Temporal workflows provide retry semantics for on-chain operations; agent-to-agent calls should handle network failures gracefully (aiohttp client + tool exceptions).
- **Telemetry**: Consider adding tracing/log aggregation across agents to observe end-to-end flows (vector query → conversation → order submission → settlement).
- **Future Enhancements**: data_agent roadmap includes broadcasting basket rebalancing events; invest_agent already imports `FetchAiAgentToAgentClient`, paving the way for push-based integrations.
