[<img src="../assets/coinbasket_banner_thin.png"/>](../assets/coinbasket_banner_thin.png)

# Coinbasket App

The Coinbasket App is a Next.js frontend for interacting with the Coinbasket API. It provides a web interface for AI-powered investment conversations, portfolio management, and trade execution on the BNB Chain.

## Prerequisites

- Node.js 22+

## Installation

From the **root of the repository**, install dependencies:

```bash
./nx install app
```

## Environment Configuration

Copy `.env.example` to `.env` and configure the variables.

```bash
cp .env.example .env
```

## Start Development

From the root of the repository:

```bash
./nx dev app
```

Open http://localhost:3000 in your browser.

## Start Production

From the root of the repository:

```bash
./nx start app
```

## Storybook

The app includes Storybook for component development and documentation.

```bash
# Start Storybook dev server
./nx storybook app
```

Open http://localhost:6006 for Storybook.

## Testing

```bash
# Run tests with Vitest
./nx test app
```

## Tech Stack

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Styling
- **Wagmi + Viem** - Web3 wallet integration
- **RainbowKit** - Wallet connection UI
- **React Query** - Data fetching and caching
- **React Hook Form + Zod** - Form handling and validation
- **Radix UI** - Accessible components
- **Vitest** - Testing
- **Storybook** - Component documentation
