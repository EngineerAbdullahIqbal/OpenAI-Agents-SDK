from agents import AsyncOpenAI , OpenAIChatCompletionsModel , set_tracing_disabled
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv
import os


set_tracing_disabled(True)

load_dotenv(find_dotenv())

api_key = os.getenv("GEMINI_API_KEY")

provider = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)

config = RunConfig(
    model=model,
    tracing_disabled=True
)