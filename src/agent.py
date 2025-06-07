from google.adk.agents.llm_agent import LlmAgent
from .prompt import ROOT_GARBAGE_AGENT_PROMPT
from .constants import MODEL
from .sub_agents.warsaw.agent import warsaw_garbage_agent
from dotenv import load_dotenv

load_dotenv()
root_agent = LlmAgent(
    model=MODEL,
    name="tony_soprano",
    description="An agent that herlps users with garbage collection queries.",
    instruction=ROOT_GARBAGE_AGENT_PROMPT,
    sub_agents=[
        warsaw_garbage_agent
    ],
)