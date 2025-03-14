from agents import Agent , Runner , AsyncOpenAI ,  OpenAIChatCompletionsModel
from typing import cast
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv
import chainlit as cl
import os
import asyncio

gemini_api_key = os.getenv("GEMINI_API_KEY")


load_dotenv(find_dotenv())

@cl.on_chat_start
async def start():

    
    external_Client = AsyncOpenAI(api_key=gemini_api_key,
                                base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

    model = OpenAIChatCompletionsModel(
        model="gemini-1.5-flash",
        openai_client=external_Client,
    )

    config = RunConfig(
        model=model,
        model_provider=external_Client,
        tracing_disabled=True,
    )
    '''Set the chat sesssion when user connects'''

    # cl.user_session.set('chat_history' , [])


    cl.user_session.set('config' , config)
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant that can help with tasks and questions.",
        model=model,
    )
    cl.user_session.set('agent' , agent)

    await cl.Message(content='Welcome To Our AI ChatBot! Ask Anything You Want!').send()


@cl.on_message
async def main(message: cl.Message):

    # Create a new message object for streaming
    msg = cl.Message(content="")
    await msg.send()


    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))

    if not agent or not config:
        await cl.Message(content="Error: Session not properly initialized. Please refresh the page.").send()
        return

    try:
        result = await Runner.run(agent, message.content, run_config=config)
        await msg.stream_token(result.final_output)
    except Exception as e:
        await cl.Message(content=f"An error occurred: {str(e)}").send()

    print(f'User: {message.content}')
    print(f"Assistant: {result.final_output if 'result' in locals() else 'Error occurred'}")


# asyncio.run(main())












