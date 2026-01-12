---
description: Iterative Development Loop for LangGraph Agents
---

# 🔄 LangGraph Dev Loop

This workflow covers starting the agent server, testing chats, monitoring terminal logs for "thoughts" and "responses", and iteratively refining the agent's logic.

## 1. Start the LangGraph Server
If not already running, start the dev server in a background terminal.
// turbo
```bash
npm run langgraph:dev
```
*Wait for "Server running at ::1:2024" to appear.*

## 2. Monitor Logs
Keep an eye on the terminal where `npm run langgraph:dev` is running. You should see:
- `💬 [CHAT] User Message`: The input received.
- `💭 [THOUGHT]`: The agent's intermediate reasoning.
- `🤖 [RESPONSE]`: The final output sent to the user.
- `🎯 [HUNT]`: Specific triggers for business discovery.

## 3. Send a Test Message
Use the test script to trigger the agent without opening the browser.
// turbo
```bash
npx ts-node scripts/test-cli-chat.ts "Hello, how can you help me today?"
```
To trigger a "Hunt" (Business Development Pipeline):
// turbo
```bash
npx ts-node scripts/test-cli-chat.ts "Hunt for B2B AI Automation agencies"
```

## 4. Verify in Langfuse
Check [Langfuse](https://us.cloud.langfuse.com) to see the full trace, including cost, latency, and standard LangChain callbacks.
*Every run is automatically traced via the `withLangfuseTracing` wrapper.*

## 5. Autonomous Iterative Improvement (Human-in-the-Loop)
This step enables the agent to autonomously find and fix issues with your approval.

### 5.1 Detect Issues
Run automated checks to find problems:
// turbo
```bash
npx tsx scripts/system-audit.ts
```
Review the JSON output for:
- Security vulnerabilities
- Missing error handling
- Performance bottlenecks
- Code quality issues

### 5.2 Analyze Test Results
Check the recent test runs for failures or unexpected behavior:
- Review Langfuse traces for errors
- Check terminal logs for exceptions
- Identify patterns in failed runs

### 5.3 Propose Fix
For each issue found:
1. **Identify Root Cause**: Analyze the code and logs
2. **Design Solution**: Plan the minimal fix
3. **Present to User**: Explain the issue and proposed fix
4. **Wait for Approval**: Get explicit user confirmation before making changes

### 5.4 Implement Fix
Once approved:
1. **Make Changes**: Edit the relevant files
2. **Auto-Reload**: Server reloads automatically
3. **Re-test**: Run test script to verify fix
// turbo
```bash
npx tsx scripts/test-cli-chat.ts "Test message for verification"
```
4. **Verify**: Check logs and Langfuse for success

### 5.5 Iterate
Repeat steps 5.1-5.4 until:
- All critical issues are resolved
- Tests pass consistently
- User is satisfied with behavior

### 5.6 Document Changes
Update relevant documentation:
- Add resolved issues to `ISSUES.md` as completed
- Update `STATUS.md` if capabilities changed
- Add notes to `docs/` if architecture changed

## 6. End-to-End Browser Testing
This step ensures the frontend and backend are working together correctly.

### 6.1 Open the App
Launch the browser and navigate to the local development environment.
// turbo
```bash
# Verify frontend is running
curl -I http://localhost:3000
```

### 6.2 Interact with UI
Use the browser subagent to:
1. Type a prompt like "Launch a lead hunt for tech startups in Austin"
2. Observe the "Thinking" state and streaming response
3. Verify that tool calls (logs) are visible if enabled
4. Check for any visual regressions or layout issues

### 6.3 Audit Browser Console & Logs
Check for runtime errors:
- Open browser devtools console logs
- Monitor terminal logs for both `agent-server` and `agent-chat-ui`
- Look for 404s, 500s, or CORS issues

### 6.4 Fix and Verify
If an issue is found:
1. Fix the code (backend or frontend)
2. Wait for HMR (Hot Module Replacement)
3. Refresh the page or re-run the interaction
4. Confirm resolution in both UI and logs

## 7. AI Reasoning Visibility Verification
This step ensures the AI's internal process is transparent to the user.

### 7.1 Verify "Thinking" Indicator
- Ensure the pulsing "Thinking..." state appears immediately after sending a message.
- Check that the duration matches the backend process time.

### 7.2 Verify Granular Status Cards (Widgets)
- Enable **'LOGS'** toggle in the UI.
- Issue a lead hunt command.
- Verify the appearance of emoji-prefixed status cards (e.g., 🎯, 🔍, ✅) in the message thread.
- Cards should appear *as the process happens*, not all at once at the end.

### 7.3 Verify Tool Logs
- Expand a tool call block in the thread.
- Verify that the raw JSON arguments and results are displayed correctly.
- Check for "View Details" to ensure the technical logs are accessible but not cluttering.

### 7.4 Consistency Check
- Compare UI status cards with terminal logs (💭 [THOUGHT], 📡 [RESEARCH]).
- Ensure the UI reflects the true state of the backend graph.
