import os 
from dotenv import load_dotenv , find_dotenv # For Loading environment variables
from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel 
from openai.types.responses import ResponseTextDeltaEvent
from agents.run import RunConfig
import asyncio
import chainlit as cl

# Load environment variables from .env file
load_dotenv(find_dotenv())

# set SECRET_KEY environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Set Externel Provider or client

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=external_client,
)


agent = Agent(
    name='Greeting Agent',
    instructions="""You are a friendly assistant that greets the user From Abdullah If Users Says Hi,
    or Hello say Hello or Hi From Abdullah.""",
    model=model
)

@cl.on_chat_start
async def start():
    '''Setting Up the chat session for user when user connects to chat'''
    run_config = RunConfig(
    model=model,
    tracing_disabled=True,
 )   

    cl.user_session.set("agent", agent)
    cl.user_session.set("config", run_config)
    cl.user_session.set("history", [])  # Initialize empty chat history

    await cl.Message(
        content="Hello! How can I help you today?"
    ).send()  # Send welcome message
    

@cl.on_message
async def main(message: cl.Message):
    '''This function is called when user sends a message to chat'''
    
    msg = cl.Message(content="")
    await msg.send()

    history = cl.user_session.get("history")
    agent : Agent = cl.user_session.get("agent")
    config : RunConfig = cl.user_session.get("config")

    history.append(
        {"role": "user", "content": message.content}
    )  # Add user message to history
    
    result = await cl.make_async(Runner.run_sync)(agent ,input=history, run_config=config)


    response_text = result.final_output
    await cl.Message(content=response_text).send()

    history.append({"role": "assistant", "content": response_text})
    # cl.user_session.set("history", history)

    
        
