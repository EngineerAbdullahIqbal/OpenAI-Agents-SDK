from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv
import chainlit as cl
import os
from typing import cast


# Load environment variables from .env file
load_dotenv(find_dotenv())

# set SECRET_KEY environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL="gemini-2.0-flash"


# Set Externel Provider or client


def setup_config():
    external_client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model = OpenAIChatCompletionsModel(
        model=MODEL,
        openai_client=external_client,
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )


    Hindi_translator = Agent(
        name='Hindi_Translator',
        instructions='Translate user query to Hindi',
        handoff_description="Specialist agent for Hindi translation",
        model=model
    )

    urdu_translator = Agent(
        name='Urdu_Translator',
        instructions='Translate user query to Urdu',        
        handoff_description="Specialist agent for Urdu translation",
        model=model
    )

    triage_agent = Agent(
        name="triage_agent",
        instructions=(
            "You are a translation agent. You use the tools given to you to translate."
            "If asked for multiple translations, you call the relevant tools in order."
            "You never translate on your own, you always use the provided tools."
        ),
        tools=[
            Hindi_translator.as_tool(
                tool_name="Hindi_Translator",
                tool_description="Translate user query to Hindi",
            ),
            urdu_translator.as_tool(
                tool_name="Urdu_Translator",
                tool_description="Translate user query to Urdu",
            ),
        ],
        model=model
    )
    
    return triage_agent, config


@cl.on_chat_start
async def start():
    triage_agent , config = setup_config()

    cl.user_session.set("chat_history" , [])

    cl.user_session.set("agent" , triage_agent)
    cl.user_session.set("config" , config)

    await cl.Message(content="Hello! How can I help you today?").send()



@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses."""
    # Send a thinking message
    msg = cl.Message(content="Thinking...")
    await msg.send()
    
    triage_agent = cast(Agent, cl.user_session.get("agent"))
    config = cast(RunConfig, cl.user_session.get("config"))

    # Retrieve the chat history from the session.
    history = cl.user_session.get("chat_history") or []

    # Append the user's message to the history.
    history.append({"role": "user", "content": message.content})

    result = await Runner.run(triage_agent, history, run_config=config)

    response_content = result.final_output

    # Update the thinking message with the actual response
    msg.content = response_content
    await msg.update()

    history.append({"role": "assistant", "content": response_content})

    cl.user_session.set("chat_history", history)

    print(f"History: {history}")