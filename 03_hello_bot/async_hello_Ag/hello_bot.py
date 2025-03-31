from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv # For Loading environment variables
import os
import asyncio

# Load environment variables from .env file
load_dotenv(find_dotenv())

# set SECRET_KEY environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL=os.getenv('MODEL')


# Set Externel Provider or client

provider = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Setting Up Our Model With "OpenAIChatCompletionsModel"

model = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=provider
)

config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True
)

async def main():

    agent = Agent(
        name='Assistant',
        instructions='Answer The User Questions and solve there queries.',
        model=model
    )

    result = await Runner.run(agent , input="what is the capital of Iran?" , run_config=config)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

