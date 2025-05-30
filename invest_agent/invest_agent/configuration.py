from environs import env


class Configuration:
    def __init__(self):
        env.read_env()

        self.agent_name = env.str("AGENT_NAME")
        self.agent_seed = env.str("AGENT_SEED")
        self.agent_port = env.int("AGENT_PORT")
        self.agent_key = env.str("AGENT_KEY")

        self.bsc_base_token_name = env.str("BSC_BASE_TOKEN_NAME")
        self.bsc_base_token_display_name = env.str("BSC_BASE_TOKEN_DISPLAY_NAME")
        self.bsc_base_token_ticker = env.str("BSC_BASE_TOKEN_TICKER")
        self.bsc_base_token_address = env.str("BSC_BASE_TOKEN_ADDRESS")

        self.bsc_rpc_url = env.str("BSC_RPC_URL")
        self.bsc_private_key = env.str("BSC_PRIVATE_KEY")

        self.data_agent_address = env.str("DATA_AGENT_ADDRESS")
        self.data_agent_key = env.str("DATA_AGENT_KEY")
        self.data_agent_url = env.str("DATA_AGENT_URL")

        self.langsmith_tracing = env.str("LANGSMITH_TRACING")
        self.langsmith_api_key = env.str("LANGSMITH_API_KEY")

        self.pancakeswap_universal_router_address = env.str(
            "PANCAKESWAP_UNIVERSAL_ROUTER_ADDRESS"
        )
        self.pancakeswap_permit2_contract_address = env(
            "PANCAKESWAP_PERMIT2_CONTRACT_ADDRESS"
        )
        self.pancakeswap_v2_router_address = env.str("PANCAKESWAP_V2_ROUTER_ADDRESS")

        self.openai_api_key = env.str("OPENAI_API_KEY")

        self.zero_x_api_url = env.str("ZERO_X_API_URL")
        self.zero_x_api_key = env.str("ZERO_X_API_KEY")
