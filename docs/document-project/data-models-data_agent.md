# Data Agent Knowledge Store

## Vector Store Configuration

- **Backend**: Qdrant (HTTP + GRPC), initialized via `QdrantLangChainSimilarityStorage`.
- **Collection**: Created on demand using `configuration.qdrant_collection`; vectors configured as 1,536-dimensional cosine embeddings (OpenAI text-embedding-3-large defaults).
- **Clients**: Both sync (`QdrantClient`) and async (`AsyncQdrantClient`) clients are instantiated to support ingestion and scrolling operations.

## Document Schema

All ingested entities are converted into `SimilarityDocument` objects with the following shape:

```json
{
  "id": "<uuid or deterministic id>",
  "page_content": "string representation of the asset or basket",
  "metadata": {
    "source": { "...domain object fields..." },
    "type": "token | basket",
    "version": <int>
  }
}
```

- `source`: retains the full token or basket payload (`Token.to_dict()` / `Basket.to_dict()`), ensuring downstream agents can rebuild domain models.
- `type`: used for filtering similarity searches (`TOKEN` vs `BASKET`).
- `version`: increments when canonical data sources change so stale documents can be rehydrated.

## Ingestion Pipelines

| Data Source | Module | Description | Document ID Strategy |
| --- | --- | --- | --- |
| PancakeSwap Token List | `pancakeswap_tokens_data_source.py` | Fetches extended token list, normalizes display names, and maps each token to a `type="token"` vector. | Deterministic UUID derived from token address (`id_generator.generate_id(address[2:])`). |
| Curated Baskets | `big4_basket_data_source.py`, `ai_basket_data_source.py`, `cmc_top_10_2025.py`, `cryptoummah_halal_basket_data_source.py`, `memecoin_mania_basket_data_source.py` | Handcrafted thematic baskets stored as `type="basket"` documents with human-readable descriptions. | Fixed UUID per basket definition. |

During agent startup (`data_agent/main.py`), `IngestDataUseCase` loads each data source and upserts content into Qdrant. Subsequent `/` similarity searches and `/basket` lookups query the store with metadata filters to return tokens or baskets matching the caller’s request.

## Access Patterns

- **Similarity Search**: `SimilarityStorage.asimilarity_search` retrieves the top 10 vectors, applying metadata filters (`Filter` + `FieldCondition`) to limit results by `type` or custom metadata (e.g., `source.ticker`).
- **Lookups by Field**: `get_by_field` scrolls through the collection to find documents where `metadata.<field>` equals a value—used for deterministic fetches (e.g., basket by ID).
- **Agent Responses**: Returned documents are normalized into protocol models (`TokenResponse`, `BasketResponse`) before being sent back to the invest agent.

## Operational Notes

- Ensure Qdrant URL, ports, and API key are supplied in `data_agent.Configuration`; missing credentials will prevent collection creation and ingestion.
- The ingestion pipeline runs on every startup; if documents already exist, Qdrant deduplicates via point IDs.
- Consider enabling Qdrant payload indexing on frequently filtered metadata fields (e.g., `metadata.type`) if the vector store grows substantially.
