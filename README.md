[<img src="./assets/coinbasket_banner_thin.png"/>](./assets/coinbasket_banner_thin.png)

# coinbasket open source ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:ASI](https://img.shields.io/badge/asi-3D8BD3)
This mono-repository contains the code for the coinbasket open source offering, which includes two main components: the invest agent and the data agent. These agents are designed to work together to manage and execute investment strategies based on data retrieved from various sources.

Please refer to the individual directories for more information on each agent:
- [data_agent](./data_agent/README.md): The data agent is responsible for retrieving relevant information based on user queries and broadcasting basket rebalancing events to the invest agent.
- [invest_agent](./invest_agent/README.md): The invest agent is responsible for managing and executing investment strategies based on data retrieved from the coinbasket data agent. It uses the Fetch.ai framework to interact with other agents and perform trades on the BNB Chain.