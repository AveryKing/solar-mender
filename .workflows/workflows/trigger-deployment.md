---
description: Trigger GitHub Actions deployment pipeline
---
# Trigger Deployment Workflow

Triggers the GitHub Actions deployment pipeline by creating an empty commit and pushing to main.

## When to Use
- After updating GitHub secrets (e.g., Langfuse keys, API tokens)
- When you want to redeploy without code changes
- To pick up environment variable changes

## Execution Steps

**Option 1: Using GitHub MCP (Recommended)**
- Use `mcp_github_create_or_update_file` to create/update a trigger file
- This automatically commits and pushes, triggering the workflow

**Option 2: Using Git**
1. **Create Empty Commit**:
   ```bash
   git commit --allow-empty -m "redeploy with updated secrets"
   ```

2. **Push to Main**:
   ```bash
   git push origin main
   ```

3. **Monitor Deployment**:
   - Check GitHub Actions: https://github.com/AveryKing/phantom-apollo/actions
   - Wait for deployment to complete
   - Verify Cloud Run service is updated

## Notes
- This creates an empty commit (no code changes)
- The deployment will use the latest GitHub secrets
- Make sure you're on the main branch before running
- Uncommitted changes won't be included (empty commit only)
