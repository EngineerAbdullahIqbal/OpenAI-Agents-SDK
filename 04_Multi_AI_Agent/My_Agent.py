from agents import Agent , Runner , function_tool , AsyncOpenAI , OpenAIChatCompletionsModel 
from agents.run import RunConfig
from typing import cast , Dict , Optional
import chainlit as cl
from dotenv import load_dotenv , find_dotenv
import requests
from bs4 import BeautifulSoup
import json
import os
from openai.types.responses import (
    ResponseFunctionCallArgumentsDeltaEvent,  # tool call streaming
    ResponseCreatedEvent, # start of new event like tool call or final answer
    ResponseTextDeltaEvent  
)


load_dotenv(find_dotenv())
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL=os.getenv('MODEL')

external_client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=os.getenv("BASE_URL"),
)

model = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=external_client,
)

def fetch_github_profile(username):
    url = f"https://github.com/EngineerAbdullahIqbal"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def extract_linkedin_profile_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
        if script_tag:
            data = json.loads(script_tag.string)
            profile = data.get("props", {}).get("pageProps", {}).get("profile", {})
            name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
            job_title = profile.get("headline", "")
            return {"name": name, "job_title": job_title}
    return {}


@function_tool
async def fetch_profile_data(url: str) -> dict:
    if "github.com" in url:
        username = url.split("/")[-1]
        return fetch_github_profile(username)
    elif "linkedin.com/in/" in url:
        return extract_linkedin_profile_data(url)
    else:
        return {"error": "Unsupported URL format"}
    


# Decorator to handle OAuth callback from GitHub
@cl.oauth_callback
def oauth_callback(
    provider_id: str,  # ID of the OAuth provider (GitHub)
    token: str,  # OAuth access token
    raw_user_data: Dict[str, str],  # User data from GitHub
    default_user: cl.User,  # Default user object from Chainlit
) -> Optional[cl.User]:  # Return User object or None
    """
    Handle the OAuth callback from GitHub
    Return the user object if authentication is successful, None otherwise
    """
    print(f"Provider: {provider_id}")  # Print provider ID for debugging
    print(f"User data: {raw_user_data}")  # Print user data for debugging

    return default_user  # Return the default user object



data_fetcher = Agent(
    name="Data Fetcher",
    instructions="""You are a data fetcher with the ability to fetch data from different sources
    Fetches data from a given URL.""",
    tools=[fetch_profile_data],
    model=model
)

personal_assistant = Agent(
    name="Personal Assistant",
    instructions="""You are my Personal Assistant. You know all information about Abdullah.
    If a user says 'Hello' or 'Hi', answer with 'Hello from Abdullah.
    - Answer in Very Humble Manner.
    - If user Ask anyting else, answer with 'I can answer only about Abdullah'.
    - Use the Data Fetcher to fetch data from different sources.""",
    handoffs=[data_fetcher],
    model=model
)


@cl.on_chat_start
async def start():
    '''Setting Up the chat session for user when user connects to chat'''
    run_config = RunConfig(
    model=model,
    tracing_disabled=True,
 )   

    cl.user_session.set("agent", personal_assistant)
    cl.user_session.set("config", run_config)
    cl.user_session.set("history", [])  # Initialize empty chat history

    await cl.Message(
        content="Hello! How can I help you today?"
    ).send()  # Send welcome message


@cl.on_message
async def handle_message(message: cl.Message):
    # Get message history from session
    history = cl.user_session.get("history", [])

    # Add user message to history
    history.append({"role": "user", "content": message.content})

    # Create a message for streaming the response
    msg = cl.Message(content="")
    await msg.send()

    # Get agent and config from session
    agent : Agent = cast(Agent , cl.user_session.get("agent"))
    config : RunConfig = cast(RunConfig , cl.user_session.get("config"))

    # Run the agent with streaming
    result = Runner.run_streamed(
        agent,
        input=history,
        run_config=config,
    )

    # Stream the tokens as they come
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await msg.stream_token(event.data.delta)

    # Add assistant response to history
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)

