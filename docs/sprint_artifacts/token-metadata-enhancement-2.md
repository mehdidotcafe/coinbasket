# Story 1.2: CoinGecko Data Source Enhancement

**Status:** Draft

---

## User Story

As a **system**,
I want the CoinGecko data source to fetch comprehensive token metadata,
So that tokens in the system have rich information for analysis and decision-making.

---

## Acceptance Criteria

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

---

## Implementation Details

### Tasks / Subtasks

1. **Enhance CoinDetailResponse model**
   - Add `categories: list[str]` field
   - Add `description: dict[str, str]` field for multi-language descriptions
   - Add `links: dict[str, list[str]]` field for various link types
   - Ensure `detail_platforms` properly captures decimal_place

2. **Update _fetch_detail method**
   - Extract categories from API response
   - Extract English description from `description.en`
   - Extract homepage URLs from `links.homepage`
   - Handle missing/optional fields gracefully with defaults

3. **Modify token mapping logic**
   - Update token creation to populate new fields
   - Set decimals from `detail_platforms.binance-smart-chain.decimal_place`
   - Map categories, description, and links to Token fields
   - Maintain backward compatibility

4. **Update version and error handling**
   - Increment `version()` method to 5 for cache invalidation
   - Add try/catch for optional field extraction
   - Maintain existing API authentication and rate limiting

5. **Add comprehensive tests**
   - Mock CoinGecko API responses with new fields
   - Test successful metadata extraction
   - Test error handling for missing fields
   - Test backward compatibility

### Technical Summary

Enhance the existing CoinGecko data source to leverage the contract detail endpoint for fetching comprehensive token metadata. This involves updating API response models, modifying data extraction logic, and ensuring robust error handling while maintaining the existing data source interface.

### Project Structure Notes

- **Files to modify:** 
  - `data_agent/data_agent/ingestion/data_source/infrastructure/bsc/coingecko_live_tokens_data_source.py`
  - `data_agent/data_agent/ingestion/data_source/infrastructure/bsc/coingecko_live_tokens_data_source_test.py` (create if doesn't exist)
- **Expected test locations:** Same directory with `*_test.py` naming
- **Estimated effort:** 3 story points
- **Prerequisites:** Story 1.1 (Enhanced Token Domain Model) must be completed

### Key Code References

**Current CoinGecko implementation:**
```python
# Existing _fetch_detail method calls contract endpoint but only extracts decimal_place
async def _fetch_detail(self, contract_address: str) -> CoinDetailResponse:
    return await self.http_request.get({
        "url": f"{self.config['coingecko_base_url']}/v3/coins/{self.bsc_id}/contract/{contract_address}",
        "headers": self.headers
    }, CoinDetailResponse)
```

**API Endpoint:** `GET /v3/coins/binance-smart-chain/contract/{contract_address}`

**API Response Fields to Extract:**
- `$.detail_platforms.binance-smart-chain.decimal_place` → decimals
- `$.categories` → categories
- `$.description.en` → description
- `$.links.homepage` → links

**Existing patterns:**
- Async HTTP requests with proper authentication
- Error handling with try/catch blocks
- Version incrementing for data structure changes
- Document ID generation using `_generate_id()`

---

## Context References

**Tech-Spec:** [tech-spec.md](../tech-spec.md) - Primary context document containing:

- Brownfield codebase analysis and existing CoinGecko integration
- Python 3.10+ async patterns and error handling
- Existing data source conventions and patterns
- Integration points with Qdrant vector storage
- Complete implementation guidance for data source enhancement

**Architecture:** Data agent ingestion pipeline feeds enhanced tokens to Qdrant for similarity search

---

## Dev Agent Record

### Agent Model Used

<!-- Will be populated during dev-story execution -->

### Debug Log References

<!-- Will be populated during dev-story execution -->

### Completion Notes

<!-- Will be populated during dev-story execution -->

### Files Modified

<!-- Will be populated during dev-story execution -->

### Test Results

<!-- Will be populated during dev-story execution -->

---

## Review Notes

<!-- Will be populated during code review -->