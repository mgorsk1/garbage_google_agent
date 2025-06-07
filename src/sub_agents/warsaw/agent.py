from google.adk.agents.llm_agent import LlmAgent

from ...constants import MODEL
from .prompt import WARSAW__GARBAGE_AGENT_PROMPT
from .tools import (
    warsaw__get_garbage_categories,
    warsaw__get_garbage_sorting_rules,
    warsaw__get_garbage_category_from_website,
    warsaw__get_garbage_category_details,
    warsaw__get_garbage_schedule,
)

warsaw_garbage_agent = LlmAgent(
    model=MODEL,
    name="warsaw_garbage_agentgi",
    description="An agent that helps users with garbage collection queries related to Warsaw city.",
    instruction=WARSAW__GARBAGE_AGENT_PROMPT,
    tools=[
        warsaw__get_garbage_sorting_rules,
        warsaw__get_garbage_category_from_website,
        warsaw__get_garbage_categories,
        warsaw__get_garbage_category_details,
        warsaw__get_garbage_schedule,
    ],
)
