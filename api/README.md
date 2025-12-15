[<img src="../assets/coinbasket_banner_thin.png"/>](../assets/coinbasket_banner_thin.png)

# coinbasket API

The coinbasket API is designed to manage and execute investment strategies based on data retrieved from different data sources. It uses the FastAPI framework to interact with the Frontend and perform trades on the BNB Chain using 0x Protocol API and Web3.py.

## Installation
### Prerequisites
Ensure you have the following dependencies installed:
- Python (>= 3.10)
- Node.js (>= 22.0.0)

Before the first run and from the root of the repository, run:
```bash
npm install
./nx install api
```
This installs Python and Javascript dependencies (if needed).

### Environment variables
#### Development mode
In the `api` directory, copy `.env.example` to `.env.local` and fill in the required environment variables. Once configured, the API is ready to run in development mode.

#### Production mode
In the `api` directory, copy `.env.example` to `.env.production` and fill in the required environment variables. Once configured, the API is ready to run in production mode.

## Development Mode
In development mode, the commands will launch:
- an anvil container (a local BNB Chain clone)
- a redoc container (for API documentation)
- a postgresql container (for storing portfolio and orders)
- a qdrant vector database container (for storing tokens and baskets)

- the API itself

This setup enables easy local development and testing, without needing to connect to a real blockchain.

You’ll also need:
- Docker
- Docker Compose

### Running in Dev Mode
From the root of the repository, run:

```bash
./nx infra api
./nx migration:run api
./nx dev api
./nx dev:worker api
```
This will install any required Python dependencies, start the necessary dev containers, run the migrations and launch the API.

⚠️ Note: If you don't start the worker, Orders won't be executed.
⚠️ Note: For quota reasons from 0x Protocol, the orders won't be actually executed on Anvil. Orders are nonetheless created and stored in the database.

## Production Mode
Use this mode to connect the API to a live blockchain for deployment.

### Running in Production

From the root of the repository, run:

```bash
./nx infra:production api
./nx migration:production:run api
./nx start api
./nx start:worker api
```
This will install Python dependencies, start the necessary production containers, run the migrations and start the API.

⚠️ Note: If you don't start the worker, Orders won't be executed.

Note: By updating the database variables of the `.env.production` file, you are able to connect the API to any postgresql database / qdrant store of your choice.
