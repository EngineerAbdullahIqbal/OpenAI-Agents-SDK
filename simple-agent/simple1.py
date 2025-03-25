import os # For setting environment variables
from dotenv import load_dotenv , find_dotenv # For Loading environment variables 
from agents import  Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel
from agents.run import RunConfig
import asyncio


# Load environment variables from .env file
load_dotenv(find_dotenv())


# Set GEMINI_API_KEY environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")



# Set Externel Provider or client

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=external_client,
)

run_config = RunConfig(
    model=model,
    tracing_disabled=True,
)

agent = Agent(
    name="Assistant",
    instructions="Answer The User Questions in All Languages.",
    model=model,
)

async def main():
    
    result = await Runner.run(agent, "Greet me In Urdu" , run_config=run_config)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())