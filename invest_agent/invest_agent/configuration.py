import uuid
from environs import env
from marshmallow.validate import OneOf


class Configuration:
    def __init__(self):
        self.agent_env = env.str(
            "AGENT_ENV",
            validate=OneOf(
                ["development", "production", "test"],
                error="AGENT_ENV must be one of: {choices}",
            ),
        )
        self.agent_name = env.str("AGENT_NAME")
        self.agent_seed = env.str("AGENT_SEED")
        self.agent_port = env.int("AGENT_PORT")
        self.agent_key = env.str("AGENT_KEY")

        self.bsc_rpc_url = env.str("BSC_RPC_URL")
        self.bsc_private_key = env.str("BSC_PRIVATE_KEY")

        self.database_user = env.str("DATABASE_USER")
        self.database_password = env.str("DATABASE_PASSWORD")
        self.database_host = env.str("DATABASE_HOST")
        self.database_port = env.int("DATABASE_PORT")

        self.data_agent_address = env.str("DATA_AGENT_ADDRESS")
        self.data_agent_key = env.str("DATA_AGENT_KEY")
        self.data_agent_url = env.str("DATA_AGENT_URL")

        self.langchain_thread_id = env.str(
            "LANGCHAIN_THREAD_ID", default=uuid.uuid4().hex
        )
        self.langsmith_tracing = env.bool("LANGSMITH_TRACING")
        self.langsmith_api_key = env.str("LANGSMITH_API_KEY")
        self.langsmith_project = env.str("LANGSMITH_PROJECT")

        self.pancakeswap_universal_router_address = env.str(
            "PANCAKESWAP_UNIVERSAL_ROUTER_ADDRESS"
        )
        self.pancakeswap_permit2_contract_address = env(
            "PANCAKESWAP_PERMIT2_CONTRACT_ADDRESS"
        )
        self.pancakeswap_v2_router_address = env.str("PANCAKESWAP_V2_ROUTER_ADDRESS")

        self.chat_provider = env.str("CHAT_PROVIDER")
        self.chat_provider_api_key = env.str("CHAT_PROVIDER_API_KEY")
        self.chat_model = env.str("CHAT_MODEL")

        self.fee_integrator_address = env.str("FEE_INTEGRATOR_ADDRESS", default=None)
        self.fee_value_in_percentage = env.decimal(
            "FEE_VALUE_IN_PERCENTAGE", default=None
        )

        self.zero_x_api_url = env.str("ZERO_X_API_URL")
        self.zero_x_api_key = env.str("ZERO_X_API_KEY")
