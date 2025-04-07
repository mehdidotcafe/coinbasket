from uagents import Agent, Context, Model
from dotenv import dotenv_values

config = dotenv_values()


coinbasket = Agent(
    name=config["AGENT_NAME"],
    seed=config["AGENT_SEED"],
    port=config["AGENT_PORT"],
    endpoint=f"http://localhost:{config['AGENT_PORT']}/submit",
)


class PromptRequest(Model):
    text: str


class PromptResponse(Model):
    text: str


@coinbasket.on_rest_post("/", PromptRequest, PromptResponse)
async def handle_post(ctx: Context, req: PromptRequest) -> PromptResponse:
    ctx.logger.info(f"Received request with text: {req.text}")
    print(req.text)

    return PromptResponse(text="Hello World")


def main():
    coinbasket.run()


if __name__ == "__main__":
    main()
