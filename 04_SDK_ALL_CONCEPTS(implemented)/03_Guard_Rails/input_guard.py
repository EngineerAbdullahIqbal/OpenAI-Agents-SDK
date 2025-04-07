from pydantic import BaseModel
from agents import Agent , Runner , input_guardrail , GuardrailFunctionOutput , RunContextWrapper , TResponseInputItem
from setup_config import google_gemini_config


class CheckCompititorOutput(BaseModel):
    is_competitor: bool
    reasoning : str


guardrail_agent = Agent(
    name="competitor_checker",
    instructions="Analyze the user query to determine if it asks about competitors. Set 'is_competitor' to True if it does (e.g., mentions a competitor’s name or products), and False otherwise. Provide a brief reasoning for your decision..",
    output_type=CheckCompititorOutput
)


@input_guardrail
async def check_competitor(
    ctx: RunContextWrapper[None] , agent: Agent , input: str | list[TResponseInputItem]
    ) -> GuardrailFunctionOutput:

    # Extract query safely from input
    if isinstance(input, list) and input and "content" in input[-1]:
        query = input[-1].get("content", "")
    else:
        query = input

    result = await Runner.run(guardrail_agent , query , context=ctx.context , run_config=google_gemini_config)

    # Optional: Debug print to inspect agent output
    print(f"Input Guardrail Result: {result.final_output}")

    return GuardrailFunctionOutput(
        output_info=result.final_output , 
        tripwire_triggered=result.final_output.is_competitor
    )