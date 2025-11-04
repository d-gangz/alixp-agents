"""
Configuration for the process agent.

Input data sources: None (configuration constants)
Output destinations: Used by agent.py functions
Dependencies: claude-agent-sdk
Key exports: SYSTEM_PROMPT, AGENT_OPTIONS
Side effects: None
"""

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

# System prompt for the agent
SYSTEM_PROMPT = """You are a helpful AI assistant. You can help with general questions and tasks. And you love cats. So sprinkle some cat facts in your responses. Create new files in the working directory."""

SUBAGENTS = {
    "explainer": AgentDefinition(
        description="Use for explaining any concepts to beginners.",
        prompt="You are a patient, detailed explainer that uses simple language and analogies to explain concepts to beginners.",
        tools=["Read", "Edit"],
        model="haiku",
    ),
    "reviewer": AgentDefinition(
        description="Use for reviewing my responses.",
        prompt="You are a friendly and helpful assistant that reviews my responses and provides feedback.",
        model="haiku",
    ),
}

# Agent configuration options
AGENT_OPTIONS = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    # system_prompt={
    #     "type": "preset",
    #     "preset": "claude_code",  # Use Claude Code's system prompt
    # },
    allowed_tools=["Read", "Grep", "Glob", "Bash", "Write", "Edit", "Skill"],
    permission_mode="default",
    model="haiku",
    cwd="/Users/gang/git-projects/alixp-agents/process_agent/working-dir",
    setting_sources=["local"],
    agents=SUBAGENTS,
)
