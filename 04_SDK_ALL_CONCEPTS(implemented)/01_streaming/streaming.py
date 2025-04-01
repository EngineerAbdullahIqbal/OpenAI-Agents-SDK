from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv # For Loading environment variables
import os
import asyncio
from typing import cast
import chainlit as cl


load_dotenv(find_dotenv())

OPENROUTER_API_KEY=os.getenv('OPENROUTER_API_KEY')
MODEL=os.getenv('MODEL')

provider = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

model = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=provider,
)

agent = Agent(
        name="Facter",
        instructions="Genertate a fact for user query.",
        model=model
    )

@cl.on_chat_start
async def start(): 
    config = RunConfig(
        model=model,
        tracing_disabled=True
    )

    cl.user_session.set("history" , [])

    cl.user_session.set("agent" , agent)
    cl.user_session.set("config" , config)

    await cl.Message(content="Hello! How can I help you today?").send()


@cl.on_message
async def main(message: cl.Message):

    
    msg = cl.Message(content="Thinking...")
    await msg.send()

    agent : Agent = cast(Agent , cl.user_session.get("agent"))
    config : RunConfig = cast(RunConfig , cl.user_session.get("config"))

    history = cl.user_session.get("history") or []

    history.append({"role": "user" , "content" : message.content})


    result = Runner.run_streamed(agent , input=history , run_config=config)

    async for event in result.stream_events():
        if event.type == 'raw_response_event' and hasattr(event.data , 'delta'):
            token = event.data.delta
            await msg.stream_token(token) 

    history.append({"role": "assistant" , "content" : msg.content})

    cl.user_session.set("history" , history)

    print(f"User : {message.content}")
    print(f"assistant : {msg.content}")



# if __name__ == "__main__":
#     asyncio.run(main())
