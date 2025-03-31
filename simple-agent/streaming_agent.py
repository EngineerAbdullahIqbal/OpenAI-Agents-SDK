import os 
from dotenv import load_dotenv , find_dotenv # For Loading environment variables
from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel 
from agents.run import RunConfig
from typing import cast
import chainlit as cl


# Load environment variables from .env file
load_dotenv(find_dotenv())

# set SECRET_KEY environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL=os.getenv('MODEL')


# Set Externel Provider or client

external_client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=os.getenv("BASE_URL"),
)

model = OpenAIChatCompletionsModel(
    model=MODEL,
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
    history = cl.user_session.get("history") or []

    history.append(
        {"role": "user", "content": message.content}
    )  # Add user message to history

    
    msg = cl.Message(content="")
    await msg.send()

    agent : Agent =  cast(Agent , cl.user_session.get("agent"))
    config : RunConfig = cast(RunConfig , cl.user_session.get("config"))

    
    try:
        print("\nCALLING_AGENT_WITH_CONTEXT" , history , "\n")
        
        result = Runner.run_streamed(agent ,input=history , run_config=config)

        async for event in result.stream_events():
            if event.type == 'raw_response_event' and hasattr(event.data , 'delta'):
                token = event.data.delta
                await msg.stream_token(token)

        history.append({"role": "assistant" , "content" : msg.content})

        cl.user_session.set("history", history)

        print(f"User : {message.content}")
        print(f"Assistant : {msg.content}")


    

    except Exception as e:
        await msg.update(content=f'Error: {str(e)}')
        print(f"Error: {str(e)}")

