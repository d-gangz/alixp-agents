<!--
Document Type: Process Documentation
Purpose: Explains how to create and run evals for the agents
Context: Created during initial project setup
Key Topics: Evaluation structure, testing agents, eval patterns
Target Use: Reference guide for writing evals
-->

# Evals

This folder contains evaluation tests for the agents.

## Structure

Each eval should test specific capabilities of the agents and measure their performance.

## Usage

Example eval structure:

```python
import sys
sys.path.append('..')
from process_agent import query_agent
import asyncio

async def test_basic_query():
    """Test that the agent can answer a simple question."""
    response = await query_agent("What is 2+2?")
    print(f"Response: {response}")
    assert "4" in response

# Run the eval
asyncio.run(test_basic_query())
```

## Running Evals

### From the evals directory:
```bash
cd evals
uv run python your_eval_file.py
```

### Using pytest (recommended):
```bash
# Install pytest if not already installed
uv add --dev pytest pytest-asyncio

# Run all evals
uv run pytest

# Run a specific eval
uv run pytest test_your_eval.py
```

## File Naming Convention

- For simple scripts: `eval_description.py`
- For pytest tests: `test_description.py`
