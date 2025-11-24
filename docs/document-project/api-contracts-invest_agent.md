# Invest Agent API Contracts

## Overview

The invest agent exposes authenticated REST endpoints (uAgents REST bridge) for conversational orchestration, portfolio insights, and order execution plumbing. All POST endpoints require the caller to supply `agent_key` credentials enforced by the `@authentication(configuration.agent_key)` decorator. Responses use Pydantic models that mirror the domain objects in `invest_agent.*`.

## Endpoint Catalog

| Path | Method | Request Model | Response Model | Description |
| --- | --- | --- | --- | --- |
| `/conversation` | POST | `PromptRequest` (wraps `QueryMessageRequest` and `agent_key`) | `MessageResponse` | Sends a user message into the LangGraph-powered conversation loop. Executes LangGraph agent, persists the exchange, and returns the assistant response (plus optional UI payload). |
| `/conversation/messages` | POST | `MessagesRequest` (agent key only) | `MessagesResponse` (list of `MessageResponse`) | Retrieves conversation history for the configured LangChain thread ID using the LangGraph SQLite checkpoint store. |
| `/asset/swap/price` | POST | `AssetSwapPriceInfoRequest` (sell asset, amount, buy asset, agent key) | `ConvertedBalanceResponse` (wrapped `BalanceResponse` pairs) | Quotes swap pricing and conversion metadata by delegating to `GetAssetSwapPriceUseCase` (ZeroX swapper + on-chain pricing). |
| `/portfolio` | POST | `PortfolioRequest` (agent key, conversion token) | `PortfolioResponse` | Returns available balance, holdings, pending orders, and totals converted into the requested denomination. Summaries come from `GetPortfolioUseCase`. |
| `/auth` | POST | `AuthRequest` (agent key) | `AuthResponse` | Lightweight probe that verifies API authentication configuration. |
| `/health` | GET | – | `HealthResponse` | Simple uptime/health heartbeat returning `status="OK"`. |
| `/openapi` | GET | – | `OpenApiResponse` (raw dict) | Emits the generated OpenAPI JSON assembled via the `@openapi` decorators around each endpoint. |

## Authentication & Error Handling Notes

- Requests without the correct `agent_key` raise a 500 response populated by `invalid_authentication_key` (OpenAPI component from `invest_agent.documentation.response`).
- Conversation endpoints open an async SQLite connection (`langgraph_db_path`) per request; failures during agent execution propagate as standard uAgents errors.
- Pricing and portfolio endpoints convert between token/basket payloads using shared `TokenRequest` and `BasketRequest` validators, ensuring basket payloads always include at least one token.

## Cross-Agent Dependencies

- `/conversation` tools (`get_tokens_from_query`, `get_baskets_from_query`, `get_all_available_baskets`) call the data agent through `agent_to_agent_client`, so upstream outages surface as tool failures within conversation traces.
- `/asset/swap/price` and `/portfolio` leverage repositories backed by Postgres via SQLAlchemy models (`orders`, `transactions`, `postings`). Ensure migrations run before invoking these endpoints in a new environment.
