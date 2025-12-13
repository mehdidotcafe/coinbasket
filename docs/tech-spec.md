# coinbasket - Technical Specification

**Author:** coinbasket
**Date:** November 24, 2025
**Project Level:** Quick Flow (Brownfield)
**Change Type:** Data Source Migration — CoinGecko API Integration
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

The current CoinGecko token data source (`CoingeckoLiveTokenListDataSource`) provides basic token information (name, symbol, address) but lacks rich metadata that would improve user experience and investment decision-making. Users need additional context about tokens including descriptions, categories, decimal precision, and project links.

**Current Limitations:**
- Token model only captures basic fields (id, name, display_name, ticker, address)
- CoinGecko API provides much richer metadata that isn't being utilized
- Missing decimal precision leads to potential calculation issues
- No project descriptions or categorization for better asset discovery

### Proposed Solution

Enhance the CoinGecko integration to fetch comprehensive token metadata using the CoinGecko contract detail endpoint and extend the Token domain model to store this additional information.

**Technical Approach:**
1. **Extend Token Model**: Add description, decimals, categories, and links fields
2. **Enhance CoinGecko Data Source**: Use `/v3/coins/{id}/contract/{contract_address}` endpoint for detailed token data
3. **Update Vector Storage**: Persist additional metadata in Qdrant for enhanced search capabilities
4. **Maintain Compatibility**: Ensure backward compatibility with existing agent communications

### Scope

**In Scope:**

- Add new fields to `protocol/token.py`: `description`, `decimals`, `categories`, `links`
- Update `CoingeckoLiveTokenListDataSource` to call contract detail endpoint
- Extract and map the following CoinGecko API fields:
  - `$.detail_platforms.binance-smart-chain.decimal_place` → Token.decimals
  - `$.categories` → Token.categories  
  - `$.description.en` → Token.description
  - `$.links.homepage` → Token.links
- Update Qdrant similarity documents to include new metadata
- Update existing tests to handle extended Token model
- Ensure data_agent and invest_agent can handle enhanced Token objects

**Out of Scope:**

- Modifying basket data sources or domain models
- Changing existing API contracts between agents
- UI/frontend changes to display new metadata
- Integration with other CoinGecko endpoints beyond contract details

---

## Implementation Details

### Source Tree Changes

**Modified Files:**
- `protocol/protocol/token.py` — Add description, decimals, categories, links fields
- `data_agent/data_agent/ingestion/data_source/infrastructure/bsc/coingecko_live_tokens_data_source.py` — Enhanced API integration
- Test files for Token model and CoinGecko data source

### Technical Approach

**1. Token Model Enhancement**
```python
# protocol/protocol/token.py additions
class Token:
    # ... existing fields ...
    description: str | None = None
    categories: list[str] = field(default_factory=list)  
    links: list[str] = field(default_factory=list)
    # Note: decimals field already exists
```

**2. CoinGecko API Integration**
- Current: Uses token list endpoint for basic token data
- Enhancement: Call contract detail endpoint `GET /v3/coins/binance-smart-chain/contract/{contract_address}`
- Extract metadata from response and populate new Token fields
- Handle API rate limiting and error cases gracefully

**3. Data Mapping**
```
CoinGecko API → Token Model
$.detail_platforms.binance-smart-chain.decimal_place → decimals (int)
$.categories → categories (list[str])
$.description.en → description (str)
$.links.homepage → links (list[str])
```

### Existing Patterns to Follow

**Domain Model Patterns:**
- Follow existing Token field initialization in `__init__`
- Update `to_dict()` method to include new fields
- Maintain backward compatibility in serialization

**Data Source Patterns:**
- Follow existing async HTTP request patterns in `CoingeckoLiveTokenListDataSource`
- Use existing error handling and authentication mechanisms
- Maintain version() increment for cache invalidation

**Testing Patterns:**
- Add test fixtures for enhanced Token objects
- Mock CoinGecko API responses with actual response structure
- Test backward compatibility with existing Token usages

### Integration Points

**Data Agent:**
- Enhanced tokens stored in Qdrant with richer metadata
- Similarity search can leverage categories and descriptions
- API responses include additional token context

**Invest Agent:** 
- Receives enhanced Token objects via agent communication
- Can display richer token information to users
- Improved investment decision support with metadata

**Protocol:**
- Shared Token model ensures consistency across agents
- Backward compatible serialization maintains existing integrations

---

## Development Context

### Relevant Existing Code

**Current Token Model (`protocol/protocol/token.py`):**
```python
class Token:
    id: str
    name: str
    display_name: str
    description: str  # Exists but unused
    ticker: str
    decimals: int  # Exists but not populated from CoinGecko
    address: str
    logo_uri: str | None = None
```

**Current CoinGecko Integration (`data_agent/.../coingecko_live_tokens_data_source.py`):**
- Uses token list endpoint for basic token discovery
- Implements proper authentication with API keys
- Has `_fetch_detail()` method that calls contract endpoint but only extracts decimal_place
- Version 4 indicates recent changes

### Dependencies

**Framework/Libraries:**
- `pydantic` — For enhanced Token model validation
- `aiohttp` / `requests` — HTTP client for CoinGecko API calls (already integrated)
- `typing` — For type hints on new list/optional fields

**Internal Modules:**
- `protocol.token` — Core Token domain model (needs enhancement)
- `data_agent.ingestion.data_source` — Base DataSource interface
- `shared.http_request` — HTTP client abstraction

### Configuration Changes

**Environment Variables (already configured):**
- `COINGECKO_BASE_URL` — API base URL
- `COINGECKO_API_KEY` — Authentication key

**No additional configuration required** — leverages existing CoinGecko API setup

### Existing Conventions (Brownfield)

**Token Field Conventions:**
- Use `str | None` for optional string fields
- Use `list[str]` for string arrays
- Initialize collections with `field(default_factory=list)` if using dataclasses
- Maintain `id`, `name`, `display_name`, `ticker`, `address` as required fields

**Data Source Conventions:**
- Implement `async get() -> list[SimilarityDocument]`
- Increment `version()` return value when data structure changes
- Use `_generate_id()` for consistent document ID generation
- Follow existing error handling patterns with try/catch

### Existing Conventions (Brownfield)

**Code Style & Standards:**
- Python 3.10+ with type hints throughout
- `snake_case` naming for functions, variables, and modules
- `PascalCase` for class names
- Poetry for dependency management with pyproject.toml
- Ruff for linting and code formatting
- Black-compatible code style (88 character line limit)

**Token Field Conventions:**
- Use `str | None` for optional string fields
- Use `list[str]` for string arrays
- Initialize collections with `field(default_factory=list)` if using dataclasses
- Maintain `id`, `name`, `display_name`, `ticker`, `address` as required fields

**Data Source Conventions:**
- Implement `async get() -> list[SimilarityDocument]`
- Increment `version()` return value when data structure changes
- Use `_generate_id()` for consistent document ID generation
- Follow existing error handling patterns with try/catch
- Use `Configuration` TypedDict for typed config parameters

**Testing Conventions:**
- Test files named `*_test.py`
- Use `pytest` fixtures for mock dependencies  
- `@mark.asyncio` for async tests
- Snapshot testing for complex data transformations
- Test both success and error scenarios
- Mock external HTTP requests using `unittest.mock.AsyncMock`

**Import Organization:**
- Standard library imports first
- Third-party imports second
- Local imports last
- Use relative imports within packages

---

## Task Breakdown & Implementation Order

### Story 1: Enhanced Token Domain Model
**File:** `protocol/protocol/token.py`

**Changes Required:**
1. Add new fields to Token class with proper typing
2. Update `__init__` method to handle new optional parameters
3. Update `to_dict()` method to include new fields
4. Update `__str__` method for better representation
5. Ensure backward compatibility for existing Token usage

### Story 2: CoinGecko Data Source Enhancement  
**File:** `data_agent/data_agent/ingestion/data_source/infrastructure/bsc/coingecko_live_tokens_data_source.py`

**Changes Required:**
1. Enhance `CoinDetailResponse` model to include new fields
2. Update `_fetch_detail()` to extract additional metadata
3. Modify token mapping to populate new Token fields
4. Add error handling for missing optional fields
5. Update `version()` to reflect data structure changes
6. Update test files and fixtures

### Implementation Dependencies:
- Story 1 must be completed before Story 2
- Story 2 depends on enhanced Token model
- Both stories should include corresponding test updates

### Deployment Considerations:
- Changes are backward compatible (new fields are optional)
- Qdrant will automatically handle enhanced similarity documents
- No agent API contract changes required
- No database migrations needed

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
