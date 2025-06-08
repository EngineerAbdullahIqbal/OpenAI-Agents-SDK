import asyncio
from agents import Agent, FunctionTool, ModelSettings, RunContextWrapper, Runner , function_tool
from pydantic import BaseModel
from config import config


class UserArgs(BaseModel):
    user_name: str
    user_age: int

async def user_schema(ctx : RunContextWrapper , args : str):
    print(f"Schema Calleld with args: {args}")
    print(type(args))
    # Simulating some processing
    parsed = UserArgs.model_validate_json(args)
    return "User Schema ! woo: " + str(parsed)

tool = FunctionTool(
    name="user_schema",
    description="process user schema.",
    params_json_schema=UserArgs.model_json_schema(),
    on_invoke_tool=user_schema,
)

# @function_tool()
# def beef_maker():
#     """Special beef maker."""
#     print("Making a beefsteak...")
#     return f"You beef is ready!"


async def main():
    agent = Agent(
        name="agent",
        instructions="You are a an test agent.",
        tools=[
            tool,
        ],
     )

    result = await Runner.run(
        starting_agent=agent,
        input="process user data , Abdullah is 30 years old.",
        run_config=config
    )
    # print(agent.tools)
    print(f"Agent Name: {result.last_agent.name}")
    print(f"Final Output: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())