from environs import env


class Configuration:
    def __init__(self):
        env.read_env()

        self.agent_name = env("AGENT_NAME")
        self.agent_seed = env("AGENT_SEED")
        self.agent_port = env.int("AGENT_PORT")
        self.agent_key = env("AGENT_KEY")

        self.qdrant_api_key = env("QDRANT_API_KEY")
        self.qdrant_collection = env("QDRANT_COLLECTION")
        self.qdrant_url = env("QDRANT_URL")

        self.openai_api_key = env("OPENAI_API_KEY")
