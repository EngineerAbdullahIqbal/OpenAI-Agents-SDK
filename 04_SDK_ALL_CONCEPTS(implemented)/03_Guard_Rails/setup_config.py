from agents import AsyncOpenAI , OpenAIChatCompletionsModel
from agents.run import RunConfig
import os
from dotenv import load_dotenv , find_dotenv # For Loading environment variables


# Load environment variables from .env file
load_dotenv(find_dotenv())



OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY")
MODEL=os.getenv('MODEL')

provider = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

model = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=provider
)

google_gemini_config = RunConfig( 
    model=model,
    model_provider=provider,
    tracing_disabled=True
)