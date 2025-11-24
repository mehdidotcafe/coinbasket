# Invest Agent Data Models

## Storage Stack Overview

- **Primary database**: PostgreSQL accessed through SQLAlchemy async sessions (`create_async_engine` in `invest_agent/invest_agent/registry.py`).
- **ORM base**: Models inherit from the shared `Base` defined in `invest_agent/database/infrastructure/sql_alchemy_base.py` and are managed by repository classes (`SqlAlchemyOrderRepository`, `SqlAlchemyTransactionRepository`, `SqlAlchemyPostingRepository`).
- **Purpose**: Capture investment intents, tries, blockchain transactions, and portfolio postings used to compute holdings and pending balances.

## Core Tables

| Table | Purpose | Key Columns |
| --- | --- | --- |
| `orders` | Stores high-level investment intents (buy/sell/swap) and their planned balances. | `id` (UUID), `parent_order_id`, serialized `sell_balance_*` & `buy_balance_*` blobs (token metadata + amounts), `type`, `asset_type`, `status`, `trigger`, optional `buy_basket_id` / `sell_basket_id`. |
| `order_tries` | Records each execution attempt using external liquidity providers. | `id`, `order_id` FK, provider metadata, serialized `buy_balance_*` fields, optional serialized `fees`, relationship to `order_try_chain_transactions`. |
| `order_try_chain_transactions` | Links on-chain transactions produced during a try. | `id`, `try_id`, `order_id`, `type`, `data`, optional `hash`, `status`, `amount`, `to_address`, optional JSONB `gas`. |
| `transactions` | Persists executed blockchain transactions, including executed balances. | `id`, serialized `sell_balance_*` and `buy_balance_*`, executed balance snapshots, `type`, `asset_type`, `created_at`, optional `transaction_hash`, `order_id`, `trigger`, optional serialized `fees`, optional basket ids, optional `parent_transaction_id`. |
| `postings` | Ledger entries derived from transactions used to compute holdings. | `id`, serialized `asset` metadata, `amount`/`amount_atomic`, `decimals`, `transaction_id`, `created_at`, `type`, `asset_type`, optional `basket_id`, optional `parent_posting_id` for hierarchical composition. |

## Relationships

- `orders` ⇄ `order_tries`: one-to-many via `OrderModel.tries` (`cascade="all, delete-orphan"`).
- `order_tries` ⇄ `order_try_chain_transactions`: one-to-many capturing each blockchain call executed while fulfilling a try.
- `orders` ⇄ `transactions`: one-to-many; each transaction belongs to a specific order.
- `transactions` ⇄ `postings`: one-to-many; postings decompose transaction effects into ledger entries that power portfolio holdings.

## Serialization Strategy

- Token and basket metadata are serialized to JSON (string columns) to preserve display names, tickers, and addresses inside each record.
- Amounts are stored both as human-readable decimals (`format(amount, "f")`) and atomic integers (`NUMERIC(78, 0)`) to avoid precision loss when interacting with on-chain values.
- Fees are stored as serialized JSON blobs produced by `Fees.serialize()` / `Fees.deserialize()`.

## Operational Considerations

- Repositories accept an optional `session` so multiple writes can share a transaction; when omitted they create a scoped session via `SqlAlchemyBaseRepository.get_session`.
- Temporal workflows and LangGraph tools assume the schema is up to date; run Alembic migrations (`alembic upgrade head`) before enabling the agent in a new environment.
- The holdings queries group postings by `asset_id`/`basket_id` and aggregate `amount_atomic` while filtering out zero or negative balances, ensuring portfolio API responses only surface meaningful holdings.
