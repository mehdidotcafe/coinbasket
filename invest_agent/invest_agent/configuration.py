from environs import env


class Configuration:
    def __init__(self):
        env.read_env()

        self.agent_name = env("AGENT_NAME")
        self.agent_seed = env("AGENT_SEED")
        self.agent_port = env.int("AGENT_PORT")

        self.bsc_base_token_name = env("BSC_BASE_TOKEN_NAME")
        self.bsc_base_token_display_name = env("BSC_BASE_TOKEN_DISPLAY_NAME")
        self.bsc_base_token_ticker = env("BSC_BASE_TOKEN_TICKER")
        self.bsc_base_token_address = env("BSC_BASE_TOKEN_ADDRESS")

        self.bsc_rpc_url = env("BSC_RPC_URL")
        self.bsc_private_key = env("BSC_PRIVATE_KEY")

        self.data_agent_address = env("DATA_AGENT_ADDRESS")

        self.langsmith_tracing = env("LANGSMITH_TRACING")
        self.langsmith_api_key = env("LANGSMITH_API_KEY")

        self.pancakeswap_universal_router_address = env(
            "PANCAKESWAP_UNIVERSAL_ROUTER_ADDRESS"
        )
        self.pancakeswap_permit2_contract_address = env(
            "PANCAKESWAP_PERMIT2_CONTRACT_ADDRESS"
        )
        self.pancakeswap_v2_router_address = env("PANCAKESWAP_V2_ROUTER_ADDRESS")

        self.openai_api_key = env("OPENAI_API_KEY")
