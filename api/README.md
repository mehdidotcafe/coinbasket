[<img src="../assets/coinbasket_banner_thin.png"/>](../assets/coinbasket_banner_thin.png)

# Coinbasket API

The Coinbasket API is a FastAPI backend for managing and executing investment strategies on the BNB Chain. It handles portfolio management, order execution via 0x Protocol, and AI-powered investment conversations using LangGraph.

## Prerequisites

- Python 3.10+
- Node.js 22+
- Docker & Docker Compose

## Installation

From the **root of the repository**, install dependencies:

```bash
npm install
./nx install api
```

## Environment Configuration

Copy `.env.example` to the appropriate environment file:

| Environment | File |
|------------|------|
| Development | `.env.local` |
| Production | `.env.production` |

Fill in the required environment variables in the copied file.

## Development

Development mode starts the following Docker containers:
- **Anvil** - Local BNB Chain fork for testing
- **PostgreSQL** - Database for portfolio and orders
- **Qdrant** - Vector database for tokens and baskets
- **ReDoc** - API documentation

### Start Development

From the root of the repository:

```bash
# Start infrastructure containers
./nx infra api

# Run database migrations
./nx migration:run api

# Start the API server (http://localhost:11111)
./nx dev api

```

> **Note**: Executing 0x PROTOCOL transaction on Anvil chain will result in your key being banned. Prefer using the real BNB Chain in production mode for testing trade execution.

### API Documentation

- ReDoc: http://localhost:11112/
- OpenAPI spec: http://localhost:11111/openapi

## Production

Production mode connects to the live BNB Chain.

### Start Production

```bash
# Start production containers
./nx infra:production api

# Run database migrations
./nx migration:production:run api

# Start the API server
./nx start api
```

> **Note**: You can connect to an external PostgreSQL/Qdrant by updating the database variables in `.env.production`.
