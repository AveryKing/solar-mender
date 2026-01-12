---
description: Debug errors in the LangGraph system using Logs and Langfuse
---
# Debug System Workflow

This workflow guides you through identifying, analyzing, and fixing runtime errors in the Antigravity system, leveraging **Langfuse** for deep observability.

**Run this workflow when**:
- The Agent Chat UI returns an error.
- A "Beast Mode" run fails.
- You see unexpected agent behavior.

---

## Execution Steps

// turbo-all
1.  **Identify the Error Source**:
    *   **UI Error**: Did the Chat UI show a 500 error or a specific message?
    *   **API Error**: Did a curl command fail?
    *   **Silent Failure**: Did a task start but never finish?

2.  **Check Server Logs**:
    *   Look at the terminal where `npm run dev:server` is running.
    *   Scan for `❌` (Error) or `⚠️` (Warning) emojis.
    *   Note the **Timestamp** and **Error Message**.

3.  **Inspect Langfuse Traces**:
    *   Go to your Langfuse Dashboard: `https://us.cloud.langfuse.com`
    *   Filter traces by the recent timestamp.
    *   **Locate the Trace**: Look for red (failed) traces or long-running (latency) traces.
    *   **Click into the Trace**:
        *   **Input**: What was sent to the agent?
        *   **Output**: What did the agent return?
        *   **Steps**: Which specific node (e.g., `research_node`, `outreach_node`) failed?
        *   **Error Detail**: Read the full stack trace in Langfuse.

4.  **Verify Environment Variables**:
    *   Open `.env` (DO NOT share secrets) and check:
        *   Are all required keys present? (`GOOGLE_SEARCH_API_KEY`, `SUPABASE_KEY`, etc.)
        *   Are `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` set?
    *   Compare with `PROJECT_IDENTITY.md` requirements.

5.  **Reproduce the Issue**:
    *   Create a minimal reproduction command.
    *   Example:
        ```bash
        curl -X POST http://localhost:8080/process-lead \
          -H "Content-Type: application/json" \
          -d '{"leadId": "DEBUG_TEST_ID", "discordToken": "mock_token"}'
        ```
    *   Run this to confirm the error persists.

6.  **Fix the Issue**:
    *   **Code Fix**: Modify the failing node or tool in `src/`.
    *   **Configuration Fix**: Update `.env` or system settings.
    *   **Data Fix**: Correct malformed data in the database.

7.  **Verify the Fix**:
    *   Re-run the reproduction command (Step 5).
    *   Check Langfuse again to ensure the new trace is green (successful).

---

## Debugging Checklist

- [ ] Error identified in logs/UI
- [ ] Trace located in Langfuse
- [ ] Failing node identified
- [ ] Reproduction case created
- [ ] Fix implemented
- [ ] Fix verified via re-run

---

## Common Issues & Fixes

| Symptom | Probable Cause | Fix |
| :--- | :--- | :--- |
| **401 Unauthorized** | Missing/Invalid Keys | Check `.env` keys for Supabase/Google. |
| **TimeoutError** | API Latency | Increase timeout in `check-logs.md` or tool config. |
| **"Cannot read property X of undefined"** | Malformed State | Check previous node's output in Langfuse. |
| **Hallucinated URLs** | Grounding inactive | Verify Vertex AI Grounding is enabled. |
