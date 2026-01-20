[<img src="./assets/coinbasket_banner_thin.png"/>](./assets/coinbasket_banner_thin.png)

# Coinbasket

Coinbasket is an open-source investment strategy management and execution platform for the BNB Chain. It provides AI-powered investment recommendations, portfolio management, and trade execution through an intuitive web interface.

## Features

- **AI Investment Advisor** - LangGraph agents with OpenAI GPT integration for intelligent investment conversations
- **Portfolio Management** - Real-time balance tracking across multiple assets
- **Trade Execution** - Plan, sign, and execute swaps using 0x Protocol and PancakeSwap
- **Asset Discovery** - Vector similarity search to find related tokens and investment baskets
- **Web3 Authentication** - Sign In With Ethereum (SIWE) for secure wallet-based authentication

## Architecture

This monorepo contains two main components:

| Component | Description |
|-----------|-------------|
| [api](./api) | Python/FastAPI backend for investment strategy execution |
| [app](./app) | Next.js frontend with React and TypeScript |

## Tech Stack

**Backend**: Python, FastAPI, Web3.py, SQLAlchemy, PostgreSQL, Qdrant, LangGraph

**Frontend**: Next.js, TypeScript, Tailwind CSS, Wagmi, RainbowKit, React Query

**Blockchain**: BNB Chain, 0x Protocol, PancakeSwap

## Prerequisites

- Python 3.10+
- Node.js 22+
- Docker & Docker Compose

## Getting Started

See the individual project READMEs for detailed setup instructions:

- [API Setup](./api/README.md)
- [App Setup](./app/README.md)

## License

[GNU Affero General Public License v3.0](./LICENSE)
