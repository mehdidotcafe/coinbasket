from environs import env


class Configuration:
    def __init__(self):
        env.read_env()

        self.agent_name = env.str("AGENT_NAME")
        self.agent_seed = env.str("AGENT_SEED")
        self.agent_port = env.int("AGENT_PORT")
        self.agent_key = env.str("AGENT_KEY")

        self.qdrant_api_key = env.str("QDRANT_API_KEY")
        self.qdrant_collection = env.str("QDRANT_COLLECTION")
        self.qdrant_url = env.str("QDRANT_URL")
        self.qdrant_port = env.int("QDRANT_PORT")
        self.qdrant_grpc_port = env.int("QDRANT_GRPC_PORT")

        self.embedding_provider_api_key = env.str("EMBEDDING_PROVIDER_API_KEY")
        self.embedding_provider_model = env.str("EMBEDDING_PROVIDER_MODEL")

        self.coingecko_base_url = env.str("COINGECKO_BASE_URL")
        self.coingecko_api_key = env.str("COINGECKO_API_KEY")
