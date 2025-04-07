from agents import Agent , Runner , RunConfig
import chainlit as cl
from typing import cast
from setup_config import google_gemini_config
from input_guard import check_competitor
from output_guard import check_opinion


@cl.on_chat_start
async def start():

    cl.user_session.set("config" , google_gemini_config)
    cl.user_session.set("history" , [])

    # First we create an agent
    agent : Agent = Agent(
        name="Customer Support Bot",
        instructions="You are a helpful customer support bot for an online store. Answer questions about products, orders, and returns. Do not discuss competitors or give personal opinions.",
        input_guardrails=[check_competitor],
        output_guardrails=[check_opinion]
    )

    cl.user_session.set("agent" , agent)

    await cl.Message(content="Hello! How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    '''This function is called when user sends a message to chat'''
    msg = cl.Message(content="Thinking...")
    await msg.send()

    agent : Agent = cast(Agent , cl.user_session.get("agent"))
    config : RunConfig = cast(RunConfig , cl.user_session.get("config"))

    history = cl.user_session.get("history") or []
    query = message.content  # Define query as the user's input ("Hi")

    history.append({"role": "user" , "content" : message.content})

    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        result = Runner.run_sync(starting_agent=agent,
                                 input=history,
                                 run_config=config)
        
        print("After Runner.run_sync")
        print(f"RAW Result: {result}")
        response_content = result.final_output
        print(f"User query: {query}")

        # Update the thinking message with the actual response
        msg.content = response_content
        await msg.update()

        # Update the session with the new history.
        cl.user_session.set("chat_history", result.to_input_list())

        # Optional: Log the interaction
        print(f"User: {message.content}")
        print(f"Assistant: {response_content}")

    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")
    
