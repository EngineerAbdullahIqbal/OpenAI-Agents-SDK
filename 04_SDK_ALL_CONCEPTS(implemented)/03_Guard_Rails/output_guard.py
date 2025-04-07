from pydantic import BaseModel
from agents import Agent , Runner , output_guardrail , GuardrailFunctionOutput , RunContextWrapper 
from setup_config import google_gemini_config

class MessageOutput(BaseModel):
    is_opinion: bool
    reasoning : str

guardrail_agent2 = Agent(
    name= "Openion Checker",
    instructions="Analyze the message to detect personal opinions (e.g., 'I think', 'I don’t think'). Set 'is_opinion' to True if an opinion is present, False otherwise. Provide a brief reasoning.",
    output_type=MessageOutput
)

@output_guardrail
async def check_opinion(ctx: RunContextWrapper , agent: Agent , output: MessageOutput) -> GuardrailFunctionOutput:
    print(f"Output : Guardrail Triggered {output}")
    result = await Runner.run(guardrail_agent2 , output , context=ctx.context , run_config=google_gemini_config)

    print(f"Result: {result}")
    print(f"Final Output: {result.final_output}")
    if result.final_output is None:
        print("Warning: final_output is None")

    if result.final_output is None:
        print("Warning: Opinion guardrail agent returned None. Assuming no opinion.")
        return GuardrailFunctionOutput(
            output_info=None,
            tripwire_triggered=False  # Default assumption: no opinion
        )

    return GuardrailFunctionOutput(
        output_info=result.final_output , 
        tripwire_triggered=result.final_output.is_opinion
    )