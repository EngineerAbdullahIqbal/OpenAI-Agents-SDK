from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel
from agents.run import RunConfig
from dotenv import load_dotenv , find_dotenv # For Loading environment variables
import os
from typing import cast
import chainlit as cl

load_dotenv(find_dotenv())

OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY")
MODEL=os.getenv("MODEL")

# Check if the API key is present; if not, raise an error
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set. Please ensure it is defined in your .env file.")


provider = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=provider
)


senior_chef = Agent(
    name="Senior Chef",
    instructions="""
    You are a senior chef with 50 years of experience in cooking, dedicated to guiding people through a wide variety of recipes and sharing your extensive knowledge of ingredients, 
    techniques, and kitchen tools. Your guidance should be clear, supportive, and tailored to the user's skill level, from beginners to experienced cooks. 
    Offer cooking tips, explain techniques, suggest substitutions, and help troubleshoot common issues. 
    Be respectful of different culinary traditions and always prioritize kitchen safety
    """,
    model=model
)


nutrition_agent = Agent(
    name="Nutrition Expert",
    instructions="""
    You are a nutrition expert with deep knowledge of dietary science, food composition, and health guidelines. 
    Your role is to:
    - Provide accurate nutritional information about foods and recipes.
    - Suggest healthy alternatives and substitutions for various dietary needs (e.g., vegan, gluten-free, low-carb).
    - Offer guidance on how to adapt recipes to meet specific health goals.
    - Answer questions about the health benefits and risks of different foods.
    Be informative, supportive, and encouraging. Help users make healthier choices without judgment, and always base your advice on scientific evidence. 
    Consider the user's individual health goals and dietary restrictions when providing recommendations.
    Note: While you can provide general nutritional guidance, remind users to consult a healthcare professional for personalized medical advice.
    """,
    model=model
)


triage_agent = Agent(
    name="Triage Specialist",
    instructions="""
    You are a triage specialist tasked with directing user queries to the appropriate agent: the Senior Chef or the Nutrition Expert.
    Analyze the user's question to determine its primary focus:
    - If the query is about cooking techniques, recipes, ingredients, kitchen tools, or culinary traditions, route it to the Senior Chef.
    - If the query is about nutritional information, dietary advice, health benefits, or adapting recipes for specific diets, route it to the Nutrition Expert.
    For questions that seem to overlap, prioritize based on the main intent:
    - If the question is primarily about how to cook something, even if it mentions health, send it to the Senior Chef.
    - If the question is primarily about the health aspects of food, even if it mentions cooking, send it to the Nutrition Expert.
    After analyzing the query, output 'ROUTE: Senior Chef' or 'ROUTE: Nutrition Expert' to indicate where the query should be directed.
    Be efficient and accurate in your routing to ensure users receive the most relevant assistance.
    """,
    handoffs=[senior_chef , nutrition_agent],
    model=model
)

# Helper function to collect the full response from an agent
async def get_full_response(agent, history, config):
    result = Runner.run_streamed(agent, history, run_config=config)
    full_response = ""
    async for event in result.stream_events():
        if event.type == 'raw_response_event' and hasattr(event.data, 'delta'):
            full_response += event.data.delta
    return full_response

@cl.on_chat_start
async def start():
    config = RunConfig(
        model=model,
        model_provider=provider,
        tracing_disabled=True
    )

    cl.user_session.set("history" , [])

    cl.user_session.set("agent" , triage_agent)
    cl.user_session.set("config" , config)


    await cl.Message(content="Hello! How can I help you today?").send()



@cl.on_message
async def main(message: cl.Message):
    '''
    This function is called when user sends a message to chat'''

    msg = cl.Message(content="Thinking...")
    await msg.send()

    history = cl.user_session.get("history") or []


    agent : Agent = cast(Agent , cl.user_session.get("agent"))
    config : RunConfig = cast(RunConfig , cl.user_session.get("config"))

    routing_decision = await get_full_response(agent, history, config)

    # Step 2: Select the appropriate agent based on the routing decision
    if "ROUTE: Senior Chef" in routing_decision:
        selected_agent = senior_chef
    elif "ROUTE: Nutrition Expert" in routing_decision:
        selected_agent = nutrition_agent
    else:
        selected_agent = triage_agent  # Fallback in case routing fails


    history.append({"role" : "user" , "content" : message.content})

    result = Runner.run_streamed(selected_agent , history , run_config=config)

    async for event in result.stream_events():
        if event.type == 'raw_response_event' and hasattr(event.data , 'delta'):
            token = event.data.delta
            await msg.stream_token(token)
        

    history.append({"role":"assistant" , "content" : msg.content})

    cl.user_session.set("history" , [])

    print(f"User : {message.content}")
    print(f"assistant : {msg.content}")
    