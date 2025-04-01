from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv # For Loading environment variables
import os

load_dotenv(find_dotenv())

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL=os.getenv('MODEL')

provider = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

model = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=provider
)

config = RunConfig( 
    model=model,
    tracing_disabled=True
)

agent = Agent(
    name='Assistant',
    instructions='Answer The User Questions in Humbel Manners.',
    model=model
)

result = Runner.run_sync(agent , input="what is the capital of Iran?" , run_config=config)

print('\nCalling Agent\n')
print(result.final_output)