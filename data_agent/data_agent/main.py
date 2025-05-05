import time

from uagents import Agent, Context

from data_agent.configuration import Configuration


thread_id = str(int(time.time()))

print(f"Thread ID: {thread_id}")

configuration = Configuration()

data_agent = Agent(
    name=configuration.agent_name,
    seed=configuration.agent_seed,
    port=configuration.agent_port,
    endpoint=f"http://localhost:{configuration.agent_port}/submit",
)


@data_agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info(f"Hello, I'm agent {configuration.agent_name}.")


def main():
    data_agent.run()


if __name__ == "__main__":
    main()
