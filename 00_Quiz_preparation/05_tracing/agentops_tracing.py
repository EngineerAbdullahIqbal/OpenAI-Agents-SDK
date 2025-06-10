from agents import Agent, Runner , function_tool
import agentops
from config import config



@function_tool
def get_weather(city: str) -> str:
    """
    get weather for city
    """
    print("--- weather tool called")
    return f"weather in {city} is sunny"


agentops.init()


agent = Agent(name="Assistant", instructions="You are a helpful assistant" , tools=[get_weather])

result = Runner.run_sync(agent, "what is weather in karachi?." , run_config=config)
print(result.final_output)

# Output:
# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.