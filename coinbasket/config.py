from environs import env


class Config:
    def __init__(self):
        env.read_env()

        self.agent_name = env("AGENT_NAME")
        self.agent_seed = env("AGENT_SEED")
        self.agent_port = env.int("AGENT_PORT")

        self.bsc_rpc_url = env("BSC_RPC_URL")
        self.bsc_private_key = env("BSC_PRIVATE_KEY")

        self.langsmith_tracing = env("LANGSMITH_TRACING")
        self.langsmith_api_key = env("LANGSMITH_API_KEY")

        self.pancakeswap_universal_router_address = env(
            "PANCAKESWAP_UNIVERSAL_ROUTER_ADDRESS"
        )

        self.openai_api_key = env("OPENAI_API_KEY")
