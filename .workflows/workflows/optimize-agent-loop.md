---
description: Run the agent in loop, log inputs/outputs, and analyze for optimization.
---

# Optimize Agent Loop Workflow

This workflow is designed to help you iteratively improve the agent's performance by running it, capturing detailed logs of its "thinking" (inputs and outputs), and having the AI assistant analyze those logs to provide optimization recommendations.

## Prerequisites

1.  **Dependencies**: Ensure `npm install` has been run.
2.  **Environment**: Ensure `.env` is configured with necessary API keys (Vertex AI, Langfuse, etc.).

## Workflow Steps

// turbo
1.  **Prepare Log Directory**:
    Create a directory to store the logs if it doesn't exist.
    ```bash
    mkdir -p logs
    ```

2.  **Start the Agent with Logging**:
    Run the LangGraph development server and redirect the output (stdout and stderr) to a log file.
    *   **Action**: Open a **SEPARATE** terminal window.
    *   **Command**:
        ```bash
        npm run langgraph:dev > logs/agent.log 2>&1
        ```
    *   *Note*: This keeps the server running in the background of that terminal. You can stop it later with `Ctrl+C`.

3.  **Interact with the Agent**:
    *   Open your browser to [http://localhost:2024](http://localhost:2024).
    *   Start a new thread or continue an existing one.
    *   Send messages to the agent (e.g., "start hunt for AI legal tools").
    *   The agent's "thinking" and responses are now being written to `logs/agent.log`.

4.  **Request Analysis**:
    *   After you have completed an interaction you want validatd, return to the AI Assistant chat.
    *   Ask the assistant to **"Analyze the agent logs"**.
    *   The assistant will read `logs/agent.log` and provide feedback on:
        *   Latency/Performance.
        *   Prompt effectiveness (System prompt vs. User input).
        *   Tool usage and "thinking" process.
        *   Potential optimizations.
