[<img src="../assets/coinbasket_banner_thin.png"/>](../assets/coinbasket_banner_thin.png)

# coinbasket invest agent ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:ASI](https://img.shields.io/badge/asi-3D8BD3)

The coinbasket invest agent is a Fetch.ai agent designed to manage and execute investment strategies based on data retrieved from the coinbasket data agent. It uses the Fetch.ai framework to interact with other agents and perform trades on the BNB Chain.

Currently, the invest agent relies on the data agent to retrieve relevant information based on user queries. Soon, it will also subscribe to basket rebalancing events broadcasted by the data agent and automatically execute trades accordingly.

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
In the `api` directory, copy `.env.example` to `.env.local` and fill in the required environment variables. Once configured, the agent is ready to run in development mode.

#### Production mode
In the `api` directory, copy `.env.example` to `.env.production` and fill in the required environment variables. Once configured, the agent is ready to run in production mode.


## Development Mode
In development mode, the agent will launch:
- an anvil container (a local BNB Chain clone)
- a redoc container (for API documentation)
- a postgresql container (for storing portfolio and orders)
- the invest agent itself

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
This will install any required Python dependencies, start the necessary dev containers, run the migrations and launch the invest agent.

⚠️ Note: If you don't start the worker, Orders won't be executed.

## Production Mode
Use this mode to connect the agent to a live blockchain for deployment.

### Running in Production

From the root of the repository, run:

```bash
./nx infra:production api
./nx migration:production:run api
./nx start api
./nx start:worker api
```
This will install Python dependencies, start the necessary production containers, run the migrations and start the invest agent.

⚠️ Note: If you don't start the worker, Orders won't be executed.

Note that by updating the database variables of the `.env.production` file, you are able to connect the agent to any postgresql database.
