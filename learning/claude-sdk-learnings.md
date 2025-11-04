<!--
Document Type: Learning Notes
Purpose: Document key learnings and insights about using the Claude Agent SDK
Context: Created while building process_agent, focusing on configuration patterns and best practices
Key Topics: Agent configuration, setting_sources behavior, subagent definitions, ClaudeAgentOptions
Target Use: Reference guide for future Claude Agent SDK projects and troubleshooting configuration issues
-->

# Claude Agent SDK Learnings

## Overview

Key insights and patterns learned while building agents with the Claude Agent SDK, focusing on configuration management, subagent definitions, and avoiding common pitfalls.

## Critical Insight: `cwd` Configuration

**CRITICAL**: The `cwd` parameter defines where the agent can write files. The agent code directory is **READ-ONLY**.

```python
AGENT_OPTIONS = ClaudeAgentOptions(
    cwd="process_agent/files",  # Agent can ONLY write here
    # ... other options
)
```

**Structure**:

```
process_agent/
├── agent.py       # READ-ONLY
├── config.py      # READ-ONLY
└── files/         # WRITABLE (cwd)
```

When agent runs `pwd`, it shows the `cwd` path. Agent cannot edit its own code, only files in `cwd`.

## Critical Insight: `setting_sources` Configuration

### The Problem with "project" Setting

When using `ClaudeAgentOptions` with `setting_sources=["project"]`:

- The user-level `~/.claude/CLAUDE.md` file **bleeds into your agent**
- All agents defined in the user-level `.claude/agents/` folder become available
- This causes unintended behavior and context pollution in your custom agent

### Attempting "project" with `.claude/` in cwd

When setting `setting_sources=["project"]` and creating `.claude/` folder in your `cwd`:

- ✅ Project-level skills in `cwd/.claude/skills/` work correctly
- ❌ **Bug**: User-level `~/.claude/CLAUDE.md` still bleeds in
- ❌ **Bug**: User-level agents from `~/.claude/agents/` still available

Expected behavior: Only project-level `.claude/` config should load.
Actual behavior: Both project-level AND user-level configs load (unintended).

### The Solution: Use "local"

```python
AGENT_OPTIONS = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    allowed_tools=["Read", "Grep", "Glob", "Bash"],
    permission_mode="acceptEdits",
    model="haiku",
    cwd="process_agent/working-dir",
    setting_sources=["local"],  # ← Use "local" to avoid user-level config bleeding in
    agents=SUBAGENTS,
)
```

**Trade-off**: Setting to `"local"` means:

- ✅ User-level CLAUDE.md and agents don't interfere
- ❌ Project-level `.claude/CLAUDE.md` won't be read
- ❌ Project-level `.claude/skills/` won't be accessible

**Workarounds for "local" limitations**:

- **Project-level CLAUDE.md**: Put instructions directly in `system_prompt` in config.py
- **Project-level skills**: Create custom CLI tools in `cwd` (working directory), as agent searches for executables there by default.

## Recommended Pattern: Define Subagents in Config

Instead of creating `.claude/agents/` folders, define agents programmatically using `AgentDefinition`:

```python
from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

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

AGENT_OPTIONS = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    allowed_tools=["Read", "Grep", "Glob", "Bash"],
    permission_mode="acceptEdits",
    model="haiku",
    cwd="process_agent",
    setting_sources=["local"],
    agents=SUBAGENTS,  # ← Pass subagents directly in config
)
```

**Benefits**:

- ✅ Everything is version-controlled in your codebase
- ✅ No hidden configuration in filesystem folders
- ✅ Clear, explicit subagent definitions
- ✅ Easy to review and modify

## Agent Architecture Pattern

### Basic Structure

```
process_agent/
├── agent.py       # Main entry point with run loop
├── config.py      # Configuration (SYSTEM_PROMPT, AGENT_OPTIONS, SUBAGENTS)
└── __init__.py
```

### Configuration File (`config.py`)

```python
"""
Configuration for the process agent.

Input data sources: None (configuration constants)
Output destinations: Used by agent.py functions
Dependencies: claude-agent-sdk
Key exports: SYSTEM_PROMPT, AGENT_OPTIONS
Side effects: None
"""

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

# Define your system prompt
SYSTEM_PROMPT = """You are a helpful AI assistant..."""

# Define subagents
SUBAGENTS = {
    "name": AgentDefinition(
        description="When to use this agent",
        prompt="System prompt for this agent",
        tools=["Read", "Edit"],  # Optional: limit tools
        model="haiku",           # Optional: use faster/cheaper model
    ),
}

# Main agent options
AGENT_OPTIONS = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    allowed_tools=["Read", "Grep", "Glob", "Bash"],
    permission_mode="acceptEdits",
    model="haiku",
    cwd="process_agent",
    setting_sources=["local"],
    agents=SUBAGENTS,
)
```

### Main Agent File (`agent.py`)

```python
"""
Interactive terminal agent using Claude Agent SDK.

Input data sources: User input from terminal
Output destinations: Terminal console output
Dependencies: claude-agent-sdk, rich for terminal UI
Key exports: run_agent(), main()
Side effects: Makes API calls to Claude, creates terminal UI
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient
from rich.console import Console
from rich.panel import Panel

from process_agent.config import AGENT_OPTIONS

async def run_agent():
    """Run the agent in interactive terminal mode."""
    console = Console()

    async with ClaudeSDKClient(options=AGENT_OPTIONS) as client:
        turn_count = 0

        while True:
            user_input = console.input(f"You (Turn {turn_count + 1}): ")

            if user_input.lower() in ["exit", "quit"]:
                break

            if user_input.lower() == "new":
                await client.disconnect()
                await client.connect()
                turn_count = 0
                continue

            if not user_input.strip():
                continue

            # Send query and receive response
            await client.query(user_input)
            turn_count += 1

            async for message in client.receive_response():
                console.print(message)

            console.print()

def main():
    """Entry point for running the agent interactively."""
    asyncio.run(run_agent())

if __name__ == "__main__":
    main()
```

## Key Learnings

### 1. LangSmith Integration

```python
from dotenv import load_dotenv
from langsmith.integrations.claude_agent_sdk import configure_claude_agent_sdk

load_dotenv()
configure_claude_agent_sdk()  # Enables automatic tracing
```

### 2. Session Management

- Use `await client.disconnect()` followed by `await client.connect()` to start fresh conversations
- Context persists across turns in the same session
- Track turn count for better UX

### 3. Tool Configuration

```python
allowed_tools=["Read", "Grep", "Glob", "Bash"]  # Main agent tools
```

Subagents can have restricted tool sets:

```python
tools=["Read", "Edit"]  # Subagent with limited tools
```

### 4. System Prompt Alternatives

You can use Claude Code's built-in system prompt:

```python
system_prompt={
    "type": "preset",
    "preset": "claude_code",  # Use Claude Code's system prompt
}
```

Or provide your own custom prompt:

```python
system_prompt="Your custom system prompt here..."
```

### 5. Permission Modes

- `acceptEdits`: Auto-accepts edit operations (useful for automation)
- `ask`: Prompts user for confirmation (safer for interactive use)

## Common Patterns

### Rich Console UI

```python
from rich.console import Console
from rich.panel import Panel

console = Console()
console.print(Panel.fit(
    "[bold cyan]Agent Name[/bold cyan]\n\n"
    "Description and commands...",
    border_style="cyan",
))
```

### Async Context Manager

Always use `async with` for proper resource management:

```python
async with ClaudeSDKClient(options=AGENT_OPTIONS) as client:
    # Your agent logic here
```

### Response Streaming

```python
async for message in client.receive_response():
    # Handle different message types
    if isinstance(message, AssistantMessage):
        # Process assistant response
    if isinstance(message, ResultMessage):
        # Handle tool results or errors
```

## Best Practices

1. **Use `setting_sources=["local"]`** to avoid user-level config pollution
2. **Define subagents in Python** using `AgentDefinition` instead of filesystem folders
3. **Add comprehensive documentation headers** to all Python files
4. **Enable LangSmith tracing** for debugging and monitoring
5. **Use Rich library** for better terminal UX
6. **Track turn count** for conversation context
7. **Provide clear exit commands** (exit, quit, new)
8. **Use haiku model** for subagents to reduce costs
9. **Limit subagent tools** to only what they need
10. **Use async context managers** for proper cleanup

## References

- See `process_agent/config.py:16-28` for subagent definition examples
- See `process_agent/agent.py:31-99` for interactive terminal agent pattern
- Claude Agent SDK documentation: [Add URL when available]
