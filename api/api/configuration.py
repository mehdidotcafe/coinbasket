from typing import Literal, cast
import uuid
import os
from environs import env
from marshmallow.validate import OneOf

Env = Literal["development", "test", "production"]


class Configuration:
    def __init__(self):
        self.app_env: Env = cast(
            Env,
            env.str(
                "APP_ENV",
                validate=OneOf(
                    ["development", "production", "test"],
                    error="APP_ENV must be one of: {choices}",
                ),
            ),
        )
        self.app_name = env.str("APP_NAME")
        self.app_key = env.str("APP_KEY")

        self.frontend_url = env.str("FRONTEND_URL")

        self.bsc_rpc_url = env.str("BSC_RPC_URL")
        self.bsc_private_key = env.str("BSC_PRIVATE_KEY")

        self.database_user = env.str("DATABASE_USER")
        self.database_password = env.str("DATABASE_PASSWORD")
        self.database_host = env.str("DATABASE_HOST")
        self.database_port = env.int("DATABASE_PORT")

        self.qdrant_api_key = env.str("QDRANT_API_KEY")
        self.qdrant_collection = env.str("QDRANT_COLLECTION")
        self.qdrant_url = env.str("QDRANT_URL")
        self.qdrant_port = env.int("QDRANT_PORT")
        self.qdrant_grpc_port = env.int("QDRANT_GRPC_PORT")

        self.embedding_provider_api_key = env.str("EMBEDDING_PROVIDER_API_KEY")
        self.embedding_provider_model = env.str("EMBEDDING_PROVIDER_MODEL")

        self.coingecko_base_url = env.str("COINGECKO_BASE_URL")
        self.coingecko_api_key = env.str("COINGECKO_API_KEY")

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

        self.small_balance_threshold = env.decimal("SMALL_BALANCE_USD_THRESHOLD")

        self.zero_x_api_url = env.str("ZERO_X_API_URL")
        self.zero_x_api_key = env.str("ZERO_X_API_KEY")

        self.temporal_port = env.int("TEMPORAL_PORT")
        self.temporal_host = env.str("TEMPORAL_HOST")

        if self.langsmith_tracing:
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            os.environ["LANGSMITH_PROJECT"] = self.langsmith_project
