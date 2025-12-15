[<img src="./assets/coinbasket_banner_thin.png"/>](./assets/coinbasket_banner_thin.png)

# coinbasket open source ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:ASI](https://img.shields.io/badge/asi-3D8BD3)
This mono-repository contains the code for the coinbasket open source offering, which includes one main component: the API. It is designed to manage and execute investment strategies based on data retrieved from various sources.

Please refer to the individual directories for more information on each component:
- [api](./api/README.md): The API is responsible for managing and executing investment strategies based on data retrieved from different data sources. It uses the FastAPI framework to interact with the Frontend and perform trades on the BNB Chain using 0x Protocol API and Web3.py.


## Running the entire stack
Once the environment variables are set up for the API, you can choose to run the entire stack in either development or production mode.

### Development mode
To run the entire stack in development mode, you can use the following quick start command:

```bash
./nx dev:all
```

This will start the API and API worker in development mode, along with their respective dependencies.
Otherwise, you can choose to start each component separately using the following commands:

```bash
./nx dev api
./nx dev:worker api
```

⚠️ Note: If you don't start the worker, Orders won't be executed.

This will start the API and API worker in development mode, along with their respective dependencies.

### Production mode
To run the entire stack in production mode, you can use the following quick start command:

```bash
./nx start:all
```

This will start the API and API worker in production mode, along with their respective dependencies.

Otherwise, you can choose to start each component separately using the following commands:

```bash
./nx start api
./nx start:worker api
```

⚠️ Note: If you don't start the worker, Orders won't be executed.

This will start the API and API worker in production mode, along with their respective dependencies.

## Interacting with the API
You can use the [Coinbasket online Frontend](https://app.coinbasket.ai) to register and interact with your API. The frontend provides a user-friendly interface to manage your investment strategies and monitor the performance of your portfolio.

⚠️ Note: Your API needs to be publicly accessible for the frontend to interact with it.