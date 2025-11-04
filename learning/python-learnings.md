<!--
Document Type: Learning Notes
Purpose: Document Python conventions and best practices learned during agent setup
Context: Created during process-agent implementation and refactoring
Key Topics: Package naming, imports, module structure, Python conventions
Target Use: Reference guide for Python project structure and naming conventions
-->

# Python Learnings

Key Python concepts and conventions learned during the agent implementation.

---

## 1. Package Naming Conventions

### The Rule
- **Hyphens (`-`)**: NOT allowed in Python package names
- **Underscores (`_`)**: Allowed and preferred

### Why?
When you import a module, Python looks for the exact folder name:
```python
from process_agent import something  # Looks for folder: process_agent/
```

If your folder is named `process-agent`, Python will fail because hyphens aren't valid in Python identifiers.

### Example
```
❌ Bad:  process-agent/     (hyphen - can't import)
✅ Good: process_agent/     (underscore - can import)
```

### When It Matters
- **Just a folder**: Hyphens are fine
- **Python package** (has `__init__.py` and you import from it): Must use underscores

---

## 2. Relative vs Absolute Imports

### Relative Imports (`.`)
```python
from .config import AGENT_OPTIONS
from .agent import run_agent
```

**Pros:**
- Shorter
- More portable within the package

**Cons:**
- Only works when the file is imported as part of a package
- Fails when you run the file directly: `python agent.py` ❌

### Absolute Imports
```python
from process_agent.config import AGENT_OPTIONS
from process_agent.agent import run_agent
```

**Pros:**
- Works when run directly: `python agent.py` ✅
- Works when imported as a module ✅
- More explicit and clear

**Cons:**
- Slightly longer
- Must match exact package name

### Best Practice
Use **absolute imports** for files that might be run directly (like `agent.py`). This provides maximum flexibility.

---

## 3. Module Structure and Separation of Concerns

### The Problem
Having multiple unrelated functions in one file makes code harder to understand:

```python
# ❌ Bad: agent.py contains BOTH
def query_agent():      # For evals
    pass

def run_agent():        # For interactive mode
    pass
```

### The Solution
**One file = One purpose**

```
✅ Good Structure:
process_agent/
├── config.py       # Configuration only
├── query.py        # Programmatic queries (evals)
├── agent.py        # Interactive terminal mode
└── __init__.py     # Package exports
```

Each file has a clear, single responsibility:
- `query.py`: Single-shot queries for evals
- `agent.py`: Interactive chat interface
- `config.py`: Shared configuration
- `__init__.py`: Public API

---

## 4. The Purpose of `__init__.py`

### What It Does
1. **Makes a folder a Python package**
2. **Controls what gets exported** when someone does `from package import *`
3. **Simplifies imports** for users

### Example

**Without `__init__.py`:**
```python
from process_agent.query import query_agent
from process_agent.agent import run_agent
```

**With `__init__.py`:**
```python
# In __init__.py
from process_agent.query import query_agent
from process_agent.agent import run_agent

__all__ = ["query_agent", "run_agent"]
```

Now users can do:
```python
from process_agent import query_agent, run_agent  # Cleaner!
```

### Best Practice
- Always include `__all__` to explicitly declare public API
- Import and re-export your public functions
- Think of it as your package's "public interface"

---

## 5. Running Python Files: Script vs Module

### Running as a Script
```bash
python agent.py
```
- Runs the file directly
- Relative imports (`.config`) will fail
- `__name__` is `"__main__"`

### Running as a Module
```bash
python -m process_agent.agent
```
- Runs as part of the package
- Both relative and absolute imports work
- `__name__` is `"process_agent.agent"`

### The `if __name__ == "__main__":` Block

```python
def main():
    """Entry point for running the agent interactively."""
    asyncio.run(run_agent())

if __name__ == "__main__":
    main()
```

**What it means:**
- "If this file is being run directly (not imported), execute `main()`"
- Allows the file to work both as a script AND as an importable module

**Use case:**
```python
# Works as a script
python agent.py          # Runs main()

# Works as a module
from process_agent.agent import run_agent  # Just imports, doesn't run main()
```

---

## 6. Configuration Management

### The Problem
Duplicated configuration in multiple places:

```python
# ❌ Bad: Duplicated in query.py
options = ClaudeAgentOptions(
    system_prompt="...",
    allowed_tools=["Read", "Grep"],
    permission_mode="acceptEdits"
)

# ❌ Bad: Same config duplicated in agent.py
options = ClaudeAgentOptions(
    system_prompt="...",
    allowed_tools=["Read", "Grep"],
    permission_mode="acceptEdits"
)
```

### The Solution
**Single source of truth** - centralized configuration:

```python
# ✅ Good: config.py
SYSTEM_PROMPT = "You are a helpful AI assistant..."

AGENT_OPTIONS = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    allowed_tools=["Read", "Grep", "Glob", "Bash"],
    permission_mode="acceptEdits",
    model="haiku"
)
```

Then both files import from the same place:
```python
from process_agent.config import AGENT_OPTIONS
```

### Benefits
- ✅ Change once, applies everywhere
- ✅ No duplication
- ✅ Easier to maintain
- ✅ Clear what the configuration is

---

## 7. Documentation Headers (Convention We're Using)

Every Python file should have a documentation header at the top:

```python
"""
Brief description of what this file does.

Input data sources: Where the data comes from
Output destinations: Where the results go
Dependencies: External packages or APIs required
Key exports: Main functions/classes that can be imported
Side effects: System interactions (API calls, file creation, etc.)
"""
```

### Benefits
- Quickly understand what a file does without reading all the code
- Helpful for LLMs and other developers
- Documents data flow and dependencies
- Makes onboarding easier

---

## 8. Making Scripts Runnable from Anywhere with Path

### The Problem
When you run a script directly with a relative path:
```bash
uv run process_agent/agent.py
```

Python sets the working directory but doesn't automatically add parent directories to `sys.path`. This causes import errors:
```python
from process_agent.config import AGENT_OPTIONS  # ❌ ModuleNotFoundError
```

### The Solution
Use `Path` to dynamically add the parent directory to Python's import path:

```python
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now this works!
from process_agent.config import AGENT_OPTIONS
```

### How It Works
```python
Path(__file__)              # Current file: /path/to/process_agent/agent.py
Path(__file__).parent       # Parent dir:   /path/to/process_agent/
Path(__file__).parent.parent # Root dir:    /path/to/
```

By adding the root directory to `sys.path`, Python can find the `process_agent` package regardless of where you run the script from.

### Benefits
- ✅ Works when run directly: `uv run process_agent/agent.py`
- ✅ Works from any directory: `cd anywhere && uv run /full/path/to/agent.py`
- ✅ Works when imported as module: `from process_agent import run_agent`
- ✅ No environment variables needed
- ✅ Portable across systems

### Best Practice
Add this pattern at the top of any script that:
1. Lives inside a package directory
2. Needs to import from that package
3. Might be run directly (not just imported)

```python
import sys
from pathlib import Path

# Always add this before your package imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Then do your imports
from your_package.module import something
```

---

## Summary: Key Takeaways

1. **Package names**: Use underscores, never hyphens
2. **Imports**: Use absolute imports for flexibility
3. **File organization**: One file = one clear purpose
4. **`__init__.py`**: Makes a folder a package and controls exports
5. **`if __name__ == "__main__"`**: Allows files to be both scripts and modules
6. **Configuration**: Centralize in a config file, import everywhere
7. **Documentation**: Add clear headers to explain purpose and data flow
8. **Path manipulation**: Use `Path` and `sys.path` to make scripts runnable from anywhere

---

## Common Patterns

### Pattern 1: Package Structure
```
my_package/
├── __init__.py      # Public API
├── config.py        # Configuration
├── core.py          # Core logic
└── cli.py           # Command-line interface
```

### Pattern 2: Dual-Purpose File
```python
# Can be imported OR run directly
def my_function():
    """Core logic."""
    pass

def main():
    """CLI entry point."""
    my_function()

if __name__ == "__main__":
    main()
```

### Pattern 3: Clean Imports
```python
# In __init__.py
from my_package.core import my_function
from my_package.cli import run_cli

__all__ = ["my_function", "run_cli"]

# Users can now do:
# from my_package import my_function, run_cli
```
