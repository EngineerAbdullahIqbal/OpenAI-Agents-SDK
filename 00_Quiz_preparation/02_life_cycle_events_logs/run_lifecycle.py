from agents import Agent , Runner , RunHooks , RunContextWrapper , function_tool
from config import config
import asyncio
from pydantic import BaseModel


class DumyData(BaseModel):
    name: str
    age: int


class CustomHook(RunHooks):

    async def on_agent_start(self, ctx: RunContextWrapper[DumyData], agent: Agent[DumyData]):
        print(f"Agent {agent.name} started with context: {ctx.context.name} and {ctx.context.age} years old.")

    async def on_agent_end(self, ctx: RunContextWrapper[DumyData], agent: Agent[DumyData], output: str):
        print(f"Agent {agent.name} ended with output: {output}")

    async def on_handoff(self, context: RunContextWrapper, from_agent: Agent[DumyData], to_agent: Agent[DumyData]):
        print(f"Handing off from {from_agent.name} to {to_agent.name}")

    async def on_tool_start(self, ctx: RunContextWrapper, agent: Agent[DumyData], tool: str):
        print(f"Agent {agent.name} started using tool: {tool}")

    async def on_tool_end(self, ctx: RunContextWrapper, agent: Agent[DumyData], tool: str, result: str):
        print(f"Agent {agent.name} finished using tool: {tool} with result: {result}")




@function_tool
def custom_tool_function(name: str, age: int) -> str:
    return f"Hello {name}, you are {age} years old."


senior_chef = Agent(
    name="senior_chef",
    instructions="You are a senior chef. Expert in cooking and pakistani dishes.",
    handoff_description="Hand off to senior chef for pakistani dishes cooking related tasks.",
)

junior_chef = Agent(
    name="junior_chef",
    instructions="You are a junior chef. Expert in cooking only karachi dishes.",
    handoff_description="Hand off to junior chef for karachi dishes cooking related tasks.",
)

async def main():

    triage_agent = Agent(
        name="triage_agent",
        instructions="You are a Triage Agent manage you sub agents and tools You have specialzed Tools and sub agents about cooking and recipes. don't answer irrelevent user Questions.",
        handoffs=[senior_chef, junior_chef],
        tools=[custom_tool_function],
    )

    user_data = DumyData(name="Abdullah" , age=20)
    result = await Runner.run(starting_agent=triage_agent , input="I want to make a Beef Biryani", context=user_data, hooks=CustomHook() , run_config=config)
    print(f"Final Output: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
