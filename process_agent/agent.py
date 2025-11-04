"""
Interactive terminal agent using Claude Agent SDK.

Input data sources: User input from terminal
Output destinations: Terminal console output
Dependencies: claude-agent-sdk, rich for terminal UI
Key exports: run_agent(), main()
Side effects: Makes API calls to Claude, creates terminal UI
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_agent_sdk import AssistantMessage, ClaudeSDKClient, ResultMessage, TextBlock
from dotenv import load_dotenv
from langsmith.integrations.claude_agent_sdk import configure_claude_agent_sdk
from rich.console import Console
from rich.panel import Panel

from process_agent.config import AGENT_OPTIONS

load_dotenv()
# Setup claude_agent_sdk with langsmith tracing
configure_claude_agent_sdk()


async def run_agent():
    """
    Run the agent in interactive terminal mode.

    Creates a chat-like interface where users can interact with the agent
    and see streaming responses.
    """
    console = Console()

    console.print(
        Panel.fit(
            "[bold cyan]Process Agent[/bold cyan]\n\n"
            "Type your questions or requests. Commands:\n"
            "  • 'exit' or 'quit' to end the session\n"
            "  • 'new' to start a new conversation",
            border_style="cyan",
        )
    )

    async with ClaudeSDKClient(options=AGENT_OPTIONS) as client:
        turn_count = 0

        while True:
            # Get user input
            console.print()
            user_input = console.input(
                f"[bold green]You[/bold green] [dim](Turn {turn_count + 1})[/dim]: "
            )

            if user_input.lower() in ["exit", "quit"]:
                console.print("\n[yellow]Ending session. Goodbye![/yellow]")
                break

            if user_input.lower() == "new":
                await client.disconnect()
                await client.connect()
                turn_count = 0
                console.print(
                    "\n[yellow]Started new conversation (previous context cleared)[/yellow]"
                )
                continue

            if not user_input.strip():
                continue

            # Send query to agent
            await client.query(user_input)
            turn_count += 1

            # Collect and display response
            console.print()
            console.print("[bold blue]Agent[/bold blue]:", end=" ")

            response_text = ""
            async for message in client.receive_response():
                console.print(message)
                # if isinstance(message, AssistantMessage):
                #     for block in message.content:
                #         if isinstance(block, TextBlock):
                #             # Stream the text to console
                #             console.print(block.text, end="")
                #             response_text += block.text

                # if isinstance(message, ResultMessage):
                #     if message.is_error:
                #         console.print(f"\n[red]Error: {message.result}[/red]")

            console.print()  # New line after response


def main():
    """Entry point for running the agent interactively."""
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()
