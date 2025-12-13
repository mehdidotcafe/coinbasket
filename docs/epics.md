# coinbasket - Epic Breakdown

**Date:** November 24, 2025
**Project Level:** Quick Flow (Brownfield)

---

## Epic 1: Token Metadata Enhancement

**Slug:** token-metadata-enhancement

### Goal

Enrich token data with comprehensive metadata from CoinGecko API to provide users with detailed token information including descriptions, categories, and project links for better investment decision-making.

### Scope

**In Scope:**
- Extend Token domain model with description, categories, decimals, and links fields
- Enhance CoinGecko data source to fetch detailed token metadata
- Update data storage and retrieval to handle enriched token data
- Maintain backward compatibility with existing agent communications

**Out of Scope:**
- Frontend/UI changes to display new metadata
- Integration with other CoinGecko endpoints beyond contract details
- Modifications to basket data sources

### Success Criteria

- Token model includes new fields: description, categories, decimals, links
- CoinGecko data source successfully fetches and populates token metadata
- Enhanced tokens are properly stored in Qdrant vector database
- All existing tests pass and new functionality is thoroughly tested
- Data agents and invest agents handle enhanced tokens without breaking changes
- API rate limiting and error handling work correctly for CoinGecko calls

### Dependencies

- Existing CoinGecko API integration and authentication
- Current Token domain model structure
- Qdrant vector storage system

---

## Story Map - Epic 1

```
Token Metadata Enhancement
├── Story 1.1: Enhanced Token Domain Model
│   └── Add metadata fields to Token class
└── Story 1.2: CoinGecko Data Source Enhancement  
    └── Fetch and populate token metadata from CoinGecko API
```

**Implementation Sequence:**
1. Story 1.1 → Story 1.2 (dependency: enhanced model required before data source changes)

---

## Stories - Epic 1

### Story 1.1: Enhanced Token Domain Model

As a **developer**,
I want the Token domain model to include rich metadata fields,
So that token objects can carry comprehensive information for better user experience and investment decisions.

**Acceptance Criteria:**

**Given** the current Token class exists in protocol/token.py
**When** I enhance the Token model
**Then** the Token class includes new fields: description (str|None), categories (list[str]), and links (list[str])
**And** the decimals field is properly utilized (already exists but unused)
**And** the __init__ method accepts new optional parameters with defaults
**And** the to_dict() method includes all new fields in serialization
**And** the __str__ method provides meaningful representation
**And** backward compatibility is maintained for existing Token usage
**And** all field types are properly annotated with type hints

**Technical Tasks:**
- Add new fields to Token class with proper typing
- Update constructor to handle new optional parameters  
- Modify to_dict() method to include new fields
- Update string representation method
- Add unit tests for enhanced Token model
- Verify backward compatibility with existing usage

### Story 1.2: CoinGecko Data Source Enhancement

As a **system**,
I want the CoinGecko data source to fetch comprehensive token metadata,
So that tokens in the system have rich information for analysis and decision-making.

**Acceptance Criteria:**

**Given** the CoingeckoLiveTokenListDataSource exists and works
**When** I enhance it to fetch detailed token metadata
**Then** it calls the CoinGecko contract detail endpoint `/v3/coins/binance-smart-chain/contract/{contract_address}`
**And** it extracts `detail_platforms.binance-smart-chain.decimal_place` to Token.decimals
**And** it extracts `categories` array to Token.categories
**And** it extracts `description.en` to Token.description
**And** it extracts `links.homepage` array to Token.links
**And** it handles missing optional fields gracefully without errors
**And** it maintains proper error handling and rate limiting
**And** it increments the version() method to reflect data changes
**And** enhanced tokens are properly stored in Qdrant with metadata

**Technical Tasks:**
- Update CoinDetailResponse model to include new API fields
- Enhance _fetch_detail() method to extract additional metadata
- Modify token mapping logic to populate new Token fields
- Add error handling for optional/missing fields
- Update version() method for cache invalidation
- Add comprehensive tests with mocked API responses
- Test error scenarios and edge cases