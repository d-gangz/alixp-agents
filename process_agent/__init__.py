"""
Process agent module for Claude Agent SDK.

Input data sources: User prompts from terminal or function arguments
Output destinations: Terminal console or function return values
Dependencies: claude-agent-sdk, rich
Key exports: run_agent(), query_agent()
Side effects: Makes API calls to Claude
"""

from process_agent.agent import run_agent
from process_agent.query import query_agent

__all__ = ["run_agent", "query_agent"]
