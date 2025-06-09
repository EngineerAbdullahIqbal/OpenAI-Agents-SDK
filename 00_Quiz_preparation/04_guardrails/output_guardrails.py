from pydantic import BaseModel
from config import config
import asyncio
from agents import Agent, GuardrailFunctionOutput , OutputGuardrailTripwireTriggered, RunContextWrapper , Runner, TResponseInputItem , output_guardrail


class OutputResponse(BaseModel):
    response : str

class ContentCheckerOutput(BaseModel):
    is_fake_content : bool
    reason : str




output_guardrail_agent = Agent(
    name="output_checker",
    instructions="You are an output guardrail agent. Your job is to check if the output is appropriate. don't allow any output that is inappropriate, harmful, or offensive. If the output is appropriate, return it as is. If not, return a message saying 'Output not allowed'.",
    output_type=ContentCheckerOutput,
)

## For Output Guardrail

@output_guardrail
async def fake_content_output_guardrail(ctx : RunContextWrapper[None] , agent: Agent , output : OutputResponse
                                   ) -> GuardrailFunctionOutput:
    result = await Runner.run(output_guardrail_agent, output.response, run_config=config)

    return GuardrailFunctionOutput(
        tripwire_triggered=result.final_output.is_fake_content,
        output_info=result.final_output
    )




video_maker_agent = Agent(
    name="video_maker",
    instructions="you are a video creation assistant help users create engaging videos.",
    output_guardrails=[fake_content_output_guardrail],
    output_type=OutputResponse
)


async def main():
    # This should trip the guardrail
    try:
        result = await Runner.run(video_maker_agent, "can u make fake video content?" , run_config=config)
        print("Guardrail didn't trip - this is unexpected")
        print(result.final_output)

    except OutputGuardrailTripwireTriggered:
        print("Fake content output guardrail tripped")

    
if __name__ == "__main__":
    asyncio.run(main())