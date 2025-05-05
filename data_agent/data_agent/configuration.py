from environs import env


class Configuration:
    def __init__(self):
        env.read_env()

        self.agent_name = env("AGENT_NAME")
        self.agent_seed = env("AGENT_SEED")
        self.agent_port = env.int("AGENT_PORT")

        self.openai_api_key = env("OPENAI_API_KEY")
