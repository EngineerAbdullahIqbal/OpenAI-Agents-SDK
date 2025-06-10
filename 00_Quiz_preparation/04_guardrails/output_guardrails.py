import json
from pydantic import BaseModel, Field
from config import config
import asyncio
from agents import Agent, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered, RunContextWrapper , Runner, TResponseInputItem , output_guardrail


class MessageOutput(BaseModel):
    reasoning: str = Field(description="Thoughts on how to respond to the user's message")
    response: str = Field(description="The response to the user's message")
    user_name: str | None = Field(description="The name of the user who sent the message, if known")


@output_guardrail
async def sensetive_data_checker(ctx: RunContextWrapper, agent: Agent, output: MessageOutput
                                )-> GuardrailFunctionOutput:
    
    
    phone_number_in_response = "650" in output.response
    phone_number_in_reasoning = "650" in output.reasoning


    return GuardrailFunctionOutput(
        output_info={
            "phone_number_in_response": phone_number_in_response,
            "phone_number_in_resoning": phone_number_in_reasoning,
        },
        tripwire_triggered= phone_number_in_response or phone_number_in_reasoning
    )



agent=Agent(
    name="assistant",
    instructions="You are a helpful assistant",
    output_type=MessageOutput,
    output_guardrails=[sensetive_data_checker],
  
)


async def main():

    await Runner.run(agent, "waht is the capital of Pakistan " , run_config=config)
    print("First Run Passed") 

    # This should trip the guardrail
    try:
        result = await Runner.run(agent, "My phone number is 650-123-4567. Where do you think I live?" , run_config=config)
        print(
            f"Guardrail didn't trip - this is unexpected : {json.dumps(result.final_output.model_dump(), indent=4)}"
            )

    except OutputGuardrailTripwireTriggered as e:
        print(f"Guardrail tripped: {e.guardrail_result.output.output_info}")

    
if __name__ == "__main__":
    asyncio.run(main())