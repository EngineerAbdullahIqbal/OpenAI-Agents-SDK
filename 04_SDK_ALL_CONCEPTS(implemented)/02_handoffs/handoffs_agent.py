from urllib import response
from agents import Agent , Runner , AsyncOpenAI, handoff , OpenAIChatCompletionsModel
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv
from typing import cast
import chainlit as cl
import os

load_dotenv(find_dotenv())

OPENROUTER_API_KEY=os.getenv('OPENROUTER_API_KEY')
MODEL=os.getenv("MODEL")

# GEMINI_API_KEY="AIzaSyBGKU70IqteZ9jVg7WHLuLnr30UfRCG9Mg"

provider = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

model = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=provider
)

# Create a specialized agent for technical support
specialized_agent = Agent(
    name="TechSupport",
    instructions="You are a technical support specialist. Handle complex technical queries.",
    model=model  
)

# Create the main support agent with tools and handoff
main_agent = Agent(
    name="SupportAssistant",
    instructions=(
        "You are a customer support assistant. Answer user queries and use the web search tool "
        "when needed. For complex technical issues, hand off to TechSupport."
    ),
    handoffs=[handoff(specialized_agent)],  # Configure handoff to the specialized agent
    model=model  
)

@cl.on_chat_start
async def start():
    '''Setting Up the chat session for user when user connects to chat'''
    run_config = RunConfig(
    model=model,
    tracing_disabled=True,
 )
    
    cl.user_session.set("history" , []) 

    cl.user_session.set("agent" , main_agent)
    cl.user_session.set("config" , run_config)

    await cl.Message(content="Hello! How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    '''This function is called when user sends a message to chat'''
    msg = cl.Message(content="Thinking...")
    await msg.send()

    agent : Agent = cast(Agent , cl.user_session.get("agent"))
    config : RunConfig = cast(RunConfig , cl.user_session.get("config"))

    history = cl.user_session.get("history") or []

    history.append({"role": "user" , "content" : message.content})


    result = await Runner.run(agent , input=history , run_config=config)

    response_content = result.final_output

    msg.content = response_content
    await msg.send()

    history.append({"role": "assistant" , "content" : result.final_output})

    cl.user_session.set("history" , history)
    print(f"History : {history}")

    print(f"User : {message.content}")
    print(f"assistant : {result.final_output}")


