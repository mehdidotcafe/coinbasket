[<img src="../assets/coinbasket_banner_thin.png"/>](../assets/coinbasket_banner_thin.png)

# coinbasket data agent ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:ASI](https://img.shields.io/badge/asi-3D8BD3)

The coinbasket data agent is a Fetch.ai agent responsible for collecting, processing, and storing data from multiple sources. It uses similarity algorithms to respond to queries from other agents—either via HTTP requests or Fetch.ai’s agent-to-agent messaging—by finding and returning relevant information.

Currently, this agent acts as a data retriever for invest agents. Soon, it will also broadcast basket rebalancing events to subscribed agents.

## Installation
### Prerequisites
Ensure the following dependencies are installed:
- Python (>= 3.10)
- Node.js (>= 22.0.0)
- Docker
- Docker Compose

Before the first run and from the root of the repository, run:
```bash
npm install
./nx install data_agent
```
This installs Python and Javascript dependencies (if needed).

### Environment variables
#### Development mode
In the `data_agent` directory, copy `.env.example` to `.env.local` and fill in the required environment variables. Once configured, the agent is ready to run in development mode.

#### Production mode
In the `data_agent` directory, copy `.env.example` to `.env.production` and fill in the required environment variables. Once configured, the agent is ready to run in production mode.


## Development Mode
In development mode, the agent spins up both a containerized Qdrant vector database and itself, streamlining development and testing—no need for an external database.


### Running in Dev Mode
From the root of the repository, run:

```bash	
./nx dev data_agent
```
This starts the Qdrant container, and launches the data agent.

## Production mode
In production mode, the agent spins up both a containerized Qdrant vector database and itself.
Note that by updating the database variables of the `.env.production` file, you are able to connect the agent to any qdrant database.


### Running in Production
From the root of the repository, run:

```bash
./nx start data_agent
```