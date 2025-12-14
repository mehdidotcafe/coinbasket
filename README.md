[<img src="./assets/coinbasket_banner_thin.png"/>](./assets/coinbasket_banner_thin.png)

# coinbasket open source ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:ASI](https://img.shields.io/badge/asi-3D8BD3)
This mono-repository contains the code for the coinbasket open source offering, which includes two main components: the invest agent and the data agent. These agents are designed to work together to manage and execute investment strategies based on data retrieved from various sources.

Please refer to the individual directories for more information on each agent:
- [data_agent](./data_agent/README.md): The data agent is responsible for retrieving relevant information based on user queries and broadcasting basket rebalancing events to the invest agent.
- [api](./api/README.md): The invest agent is responsible for managing and executing investment strategies based on data retrieved from the coinbasket data agent. It uses the Fetch.ai framework to interact with other agents and perform trades on the BNB Chain.

## Running the entire stack
Once the environment variables are set up for both agents, you can choose to run the entire stack in either development or production mode.

### Development mode
To run the entire stack in development mode, you can use the following quick start command:

```bash
./nx dev:all
```

This will start the data agent, invest agent and invest agent worker in development mode, along with their respective dependencies.

Otherwise, you can choose to start each component separately using the following commands:

```bash
./nx dev data_agent
./nx dev api
./nx dev:worker api
```

⚠️ Note: If you don't start the worker, Orders won't be executed.

This will start both the data agent and invest agent in development mode, along with their respective dependencies.

### Production mode
To run the entire stack in production mode, you can use the following quick start command:

```bash
./nx start:all
```

This will start the data agent, invest agent and invest agent worker in production mode, along with their respective dependencies.

Otherwise, you can choose to start each component separately using the following commands:

```bash
./nx start data_agent
./nx start api
./nx start:worker api
```

⚠️ Note: If you don't start the worker, Orders won't be executed.

This will start both the data agent and invest agent in production mode, along with their respective dependencies.

## Interacting with the agents
You can use the [Coinbasket online Frontend](https://app.coinbasket.ai) to register and interact with your invest agent. The frontend provides a user-friendly interface to manage your investment strategies and monitor the performance of your portfolio.

⚠️ Note: Your invest agent needs to be publicly accessible for the frontend to interact with it.
