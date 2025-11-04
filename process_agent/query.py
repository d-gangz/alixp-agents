"""
Single query function for running evals and programmatic usage.

Input data sources: User prompts passed as function arguments
Output destinations: Returns string response
Dependencies: claude-agent-sdk
Key exports: query_agent()
Side effects: Makes API calls to Claude
"""

import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_agent_sdk import AssistantMessage, ClaudeSDKClient, TextBlock
from dotenv import load_dotenv
from langsmith.integrations.claude_agent_sdk import configure_claude_agent_sdk

from process_agent.config import AGENT_OPTIONS

load_dotenv()

# Setup claude_agent_sdk with langsmith tracing
configure_claude_agent_sdk()


async def query_agent(prompt: str) -> str:
    """
    Query the agent with a single prompt and return the response.

    This function is designed for running evals - it takes a prompt
    and returns the agent's text response as a string.

    Args:
        prompt: The user's question or request

    Returns:
        The agent's response as a string
    """
    response_text = ""

    async with ClaudeSDKClient(options=AGENT_OPTIONS) as client:
        await client.query(prompt)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text

    return response_text
