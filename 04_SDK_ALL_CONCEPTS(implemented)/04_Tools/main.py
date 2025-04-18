from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel , function_tool
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv # For Loading environment variables
from duckduckgo_search import DDGS
import chainlit as cl
import os
from typing import cast


# Load environment variables from .env file
load_dotenv(find_dotenv())

OPENROUTER_API_KEY=os.getenv('OPENROUTER_API_KEY')
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "mistralai/mistral-small-3.1-24b-instruct:free"


provider = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
)

model = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=provider,
)


@function_tool
def get_news_articles(topic):
    print(f"Running DuckDuckGo news search for {topic}...")
    
    # DuckDuckGo search
    ddg_api = DDGS()
    results = ddg_api.text(f"{topic} ", max_results=5)
    if results:
        news_results = "\n\n".join([f"Title: {result['title']}\nURL: {result['href']}\nDescription: {result['body']}" for result in results])
        print(news_results)
        return news_results
    else:
        return f"Could not find news results for {topic}."




content_planner_agent = Agent(
    name="Content Planner",
    instructions="You are tasked with planning an engaging and informative blog post on {topic}. Your goal is to gather accurate, up-to-date information and structure the content",
    tools=[get_news_articles],
    model=model
)


writer_agent = Agent(
    name="Technical content writer",
    instructions="You are the technical content writer assigned to create a detailed and factually accurate blog post on: {topic}",
    model=model
)


triage_agent = Agent(
    name="Triage Agent",    
    instructions="You are a triage agent. Your job is to triage user queries and assign them to the appropriate agent If user want to write blog post then route it to content planner agent and if user want to write technical content then route it to writer agent if user simple greet hi so answer in manners e:g. Hello How can I help u.",
    model=model,
    handoffs=[content_planner_agent, writer_agent],
)

@cl.on_chat_start
async def start():
    config = RunConfig(
        model=model,
        tracing_disabled=True
    )


    cl.user_session.set("history" , [])

    cl.user_session.set("agent" , triage_agent)
    cl.user_session.set("config" , config)


    await cl.Message(content="Hello! How can I help you today?").send()



@cl.on_message
async def main(message: cl.Message):
    """Procees InComming Messages ang Generate response"""

    msg = cl.Message(content="Thinking...")
    await msg.send()

    agent :Agent = cast(Agent , cl.user_session.get("agent"))
    config : RunConfig = cast(RunConfig , cl.user_session.get("config"))

    history = cl.user_session.get("history") or []

    history.append({"role" : "user" , "content" : message.content})


    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history , "\n")
        
        result = Runner.run_sync(agent , history , run_config=config)

        response_content = result.final_output

        msg.content = response_content
        await msg.update()

        history.append({"role" : "assistant" , "content" : response_content})


        cl.user_session.set("Chat_History" , history)

        print(f"User : {message.content}")
        print(f"Assistant : {response_content}")


    except Exception as e:
        msg.content = f"Error : {str(e)}"
        await msg.update()
        print(f"Erorr : {str(e)}")

    






