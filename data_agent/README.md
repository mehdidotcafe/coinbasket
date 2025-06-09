[<img src="../assets/coinbasket_banner_thin.png"/>](../assets/coinbasket_banner_thin.png)

# coinbasket data agent ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:ASI](https://img.shields.io/badge/asi-3D8BD3)

The coinbasket data agent is a Fetch.ai agent responsible for collecting, processing, and storing data from multiple sources. It uses similarity algorithms to respond to queries from other agents—either via HTTP requests or Fetch.ai’s agent-to-agent messaging—by finding and returning relevant information.

Currently, this agent acts as a data retriever for invest agents. Soon, it will also broadcast basket rebalancing events to subscribed agents.

## Installation
### Prerequisites
Ensure the following dependencies are installed:
- Python (>= 3.10)
- Node.js (>= 22.0.0)

### Environment variables
In the `data_agent` directory, copy `.env.example` to `.env` and fill in the required variables. Once configured, the agent will be ready to run in either development or production mode.


## Dev mode
In development mode, the agent spins up both a containerized Qdrant vector database and itself, streamlining development and testing—no need for an external database.

Make sure you also have:

- Docker
- Docker Compose

### Running in Dev Mode
From the root of the repository, run:

```bash	
./nx dev data_agent
```
This installs Python dependencies (if needed), starts the Qdrant container, and launches the data agent.

## Production mode
Production mode is intended for deployments where you already have a Qdrant instance running. In this mode, the agent connects to your existing database and doesn’t start any containers.

### Running in Production
From the root of the repository, run:

```bash
./nx start data_agent
```

This installs Python dependencies (if needed) and starts the data agent.




