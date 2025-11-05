# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an experimentation project for the Claude Agent SDK. The main concept is **one folder per agent type** - each agent implementation lives in its own directory with its own configuration, interfaces, and workspace.

## Project Structure

```
alixp-agents/
├── <agent_name>/          # One folder per agent
│   ├── config.py          # Agent configuration (system prompt, tools, subagents)
│   ├── agent.py           # Interactive terminal interface (optional)
│   ├── query.py           # Programmatic interface for evals (optional)
│   └── working-dir/       # Agent workspace for file operations
├── evals/                 # Shared evaluation scripts
├── learning/              # Learning notes and experiments
└── reference/             # Reference materials
```

**Current agents:**

- `process_agent/`: Example agent with interactive and programmatic interfaces

## Development Commands

### Running an Agent

```bash
# Interactive mode (if agent has agent.py)
uv run python <agent_name>/agent.py

# Example
uv run python process_agent/agent.py
```

### Running Evals

```bash
cd evals
uv run python your_eval_file.py

# With pytest
uv run pytest
```

### Dependency Management

```bash
uv sync                    # Install all dependencies
uv add package-name        # Add runtime dependency
uv add --dev package-name  # Add dev dependency
```

### Type Checking and Linting

```bash
uv run mypy <agent_name>/  # Type checking
uv run ruff check .        # Linting
uv run ruff format .       # Format code
```

## Standard Agent Structure

Each agent folder typically contains:

**`config.py`**: Central configuration

- `SYSTEM_PROMPT`: Agent personality and behavior
- `AGENT_OPTIONS`: ClaudeAgentOptions (tools, permissions, model, cwd)
- `SUBAGENTS`: Optional AgentDefinition objects for delegation

**`agent.py`**: Interactive interface (optional)

- Terminal-based chat interface using Rich for UI
- Streaming responses via `client.receive_response()`
- Multi-turn conversation management

**`query.py`**: Programmatic interface (optional)

- Single query function for evals: `async def query_agent(prompt: str) -> str`
- Returns text-only response for evaluation workflows

**`working-dir/`**: Agent workspace

- Isolated directory for agent file operations
- Prevents accidental modifications to core project files

## Claude Agent SDK Patterns

### LangSmith Integration

Call `configure_claude_agent_sdk()` in agent files to enable automatic tracing:

```python
from langsmith.integrations.claude_agent_sdk import configure_claude_agent_sdk
configure_claude_agent_sdk()
```

### Subagent Configuration

Define in `config.py`:

```python
SUBAGENTS = {
    "subagent_name": AgentDefinition(
        description="When to use this subagent",
        prompt="System prompt for subagent",
        tools=["Read", "Edit"],  # Allowed tools
        model="haiku",
    ),
}
```

### Async Architecture

All agent code uses async/await:

```python
async with ClaudeSDKClient(options=AGENT_OPTIONS) as client:
    await client.query(prompt)
    async for message in client.receive_response():
        # Handle streaming messages
```

### Conversation State Management

- State persists across `client.query()` calls within same connection
- Reset: `await client.disconnect()` + `await client.connect()`

## Environment Variables

Create `.env` file:

- `ANTHROPIC_API_KEY`: Required for Claude API access
- `LANGSMITH_API_KEY`: Optional for LangSmith tracing

## Creating New Agents

1. Create new folder: `<agent_name>/`
2. Add `config.py` with SYSTEM_PROMPT and AGENT_OPTIONS
3. Optionally add `agent.py` (interactive) and/or `query.py` (programmatic)
4. Create `working-dir/` subdirectory for agent workspace
5. Set `cwd` in AGENT_OPTIONS to point to working-dir

## Reference Implementation

See `process_agent/` for a complete example with:

- Interactive terminal interface with Rich UI
- Programmatic query function for evals
- Subagent delegation (explainer, reviewer)
- LangSmith tracing integration

## Python Import Patterns

1. Always add project root to `sys.path` for cross-agent/folder imports
