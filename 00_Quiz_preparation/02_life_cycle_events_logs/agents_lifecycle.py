import asyncio
from dataclasses import dataclass
from typing import Any
from agents import Agent, RunContextWrapper , Runner , function_tool , AgentHooks
from pydantic import BaseModel
from config import config




class TeaIngredients(BaseModel):
    """Class to hold tea ingredients."""
    kashmiri_chai: str
    black_tea: str
    green_tea: str


class AgentsHooks(AgentHooks):
    """Custom hooks for the tea making agent."""
    def __init__(self , display_name:str):
        self.event_counter : int = 0
        self.display_name : str = display_name

    

    async def on_start(self, context: RunContextWrapper, agent: Agent):
        self.event_counter += 1
        print(f"Event Counter: {self.event_counter}")
        print(f" ({self.display_name}) ({self.event_counter}) Agent : ({agent.name}) Started")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any):
        self.event_counter += 1
        print(f"Event Counter: {self.event_counter}")
        print(f"({self.display_name}) ({self.event_counter}) Tea making agent: ({agent.name}) finished with output: ({output})")

    async def on_handoff(self, context: RunContextWrapper, agent: Agent , source: Agent):
        self.event_counter += 1
        print(f"Event Counter: {self.event_counter}")
        print(f"({self.display_name}) ({self.event_counter}) Handing off from ({source.name}) to ({agent.name})")

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: str):
        self.event_counter += 1
        print(f"Event Counter: {self.event_counter}")
        print(f"({self.display_name}) ({self.event_counter})  Tool: ({tool}) for agent: ({agent.name}) started")

    async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool: str, result: str):
        self.event_counter += 1
        print(f"Event Counter: {self.event_counter}")
        print(f"({self.display_name}) ({self.event_counter})  Tool: ({tool}) for agent: ({agent.name}) finished with result: ({result})")





### --- Tea Making  --- ###

### ---- Tools ------ ###

### ----- Tea Making  ----- ###


@function_tool
async def kashmiri_chai_maker():
    """Function to simulate making Kashmiri Chai."""
    print("Making Kashmiri Chai...")
    await asyncio.sleep(2)  # Simulate time taken to make tea
    return "Kashmiri Chai is ready!"

@function_tool
async def black_tea_maker():
    """Function to simulate making Black Tea."""
    print("Making Black Tea...")
    await asyncio.sleep(1)  # Simulate time taken to make tea
    return "Black Tea is ready!"

@function_tool
async def green_tea_maker():
    """Function to simulate making Green Tea."""
    print("Making Green Tea...")
    await asyncio.sleep(1)  # Simulate time taken to make tea
    return "Green Tea is ready!"


### --- Coffee Making Agent Tools --- ###

@function_tool
async def espresso_maker():
    """Function to simulate making Espresso."""
    print("Making Espresso...")
    await asyncio.sleep(1)  # Simulate time taken to make coffee
    return "Espresso is ready!"

@function_tool
async def cappuccino_maker():
    """Function to simulate making Cappuccino."""
    print("Making Cappuccino...")
    await asyncio.sleep(2)
    return "Cappuccino is ready!"

@function_tool
async def latte_maker():
    """Function to simulate making Latte."""
    print("Making Latte...")
    await asyncio.sleep(2)
    return "Latte is ready!"


tea_maker = Agent(
    name="tea_maker",
    instructions="You are a tea maker. Expert in making different types of tea.",
    handoff_description="Hand off to tea maker for tea making related tasks.",
    tools=[
        kashmiri_chai_maker,
        black_tea_maker,    
        green_tea_maker,
    ],
    hooks=AgentsHooks(display_name="Tea Maker Agent"),
)

coffee_maker = Agent(
    name="coffee_maker",
    instructions="You are a coffee maker. Expert in making different types of coffee.",
    handoff_description="Hand off to coffee maker for coffee making related tasks.",
    tools=[
        espresso_maker,
        cappuccino_maker,
        latte_maker,
    ],
    hooks=AgentsHooks(display_name="Coffee Maker Agent"),
)

async def main():
    triage_agent = Agent(
        name="triage_agent",
        instructions="You are a Triage Agent manage you sub agents You have specialzed Tools and sub agents about Tea and Coffee. don't answer irrelevent user Questions.",
        handoffs=[tea_maker, coffee_maker],
        hooks=AgentsHooks(display_name="Triage Agent"),
    )

    tea_data = TeaIngredients(
        kashmiri_chai="Kashmiri Chai ingredients",
        black_tea="Black Tea ingredients",
        green_tea="Green Tea ingredients"
    )

    result = await Runner.run(
        starting_agent=triage_agent,
        input="I want to make a Cappuccino",
        context=tea_data, 
        run_config=config
    )

    print(f"Final Output: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())