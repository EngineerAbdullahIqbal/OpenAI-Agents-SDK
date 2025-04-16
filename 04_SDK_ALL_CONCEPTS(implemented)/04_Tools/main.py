from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv # For Loading environment variables
from agents.tools import functions_tool
import os
from typing import cast


# Load environment variables from .env file
load_dotenv(find_dotenv())

GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')

provider = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider,
)


