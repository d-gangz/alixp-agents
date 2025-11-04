ok based on reference/agent-sdk.md, this has the documentation on how to use the Claude Agent SDK.

Note that I have already installed the `claude-agent-sdk` using the installation command. so you dont have to do it.

Here are my requirements:

1. I want to create a folder called `process-agent` in the root directory. inside, help me create the most basic agent using the claude agent sdk (read the reference/agent-sdk.md to know how to do it).

- In this folder, I need to help me set up such that I can run a cloud vision inside. Put a super simple system prompt and allow me to run in my terminal such that it creates a chat-like interface. Then I can check with it and see what is being streamed out. That kind of thing. Just a super simple agent first. you can use the `rich` package/module to create like a terminal UI.
- The agent should also be allowed to be exposed as a function where I can run my evals. so it should allow me to run a query so that I can see its output.

In the future I will be creating more agents. so each agent will be in a folder so that I can test each agent separately.

2. then create a folder called `evals`. this will hold all the evals stuff.
