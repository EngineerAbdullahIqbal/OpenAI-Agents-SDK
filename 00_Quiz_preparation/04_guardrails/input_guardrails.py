from pydantic import BaseModel
from config import config
import asyncio
from agents import Agent, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, RunContextWrapper , Runner, TResponseInputItem, function_tool, input_guardrail, output_guardrail


class OutputResponse(BaseModel):
    response : str

class ContentCheckerOutput(BaseModel):
    is_fake_content : bool
    reason : str

guard_rail_agent = Agent(
    name="fake_content_checker",
    instructions="You are a content guardrail agent. Your job is to check if the content is appropriate. don't allow any content that is inappropriate, harmful, or offensive. If the content is appropriate, return it as is. If not, return a message saying 'Content not allowed'.",
    output_type=ContentCheckerOutput,
)

@input_guardrail
async def fake_content_guardrail(ctx : RunContextWrapper[None] , agent: Agent , input : str | list[TResponseInputItem]
                          )-> GuardrailFunctionOutput:
    result = await Runner.run(guard_rail_agent, input=input, run_config=config)

    return GuardrailFunctionOutput(
        tripwire_triggered=result.final_output.is_fake_content,
        output_info=result.final_output
    )


video_maker_agent = Agent(
    name="video_maker",
    instructions="you are a video creation assistant help users create engaging videos.",
    input_guardrails=[fake_content_guardrail],
)


async def main():
    # This should trip the guardrail
    try:
        result = await Runner.run(video_maker_agent, "can u make a fake video about politics matters?" , run_config=config)
        print("Guardrail didn't trip - this is unexpected")
        print(result.final_output)

    except InputGuardrailTripwireTriggered:
        print("Fake content guardrail tripped")

    
if __name__ == "__main__":
    asyncio.run(main())