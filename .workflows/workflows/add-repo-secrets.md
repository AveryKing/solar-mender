---
description: Workflow for adding repository secrets using the GitHub CLI
---

This workflow explains how to add or update GitHub Repository Secrets using the GitHub CLI (`gh`).

### Prerequisites
- GitHub CLI (`gh`) installed: `brew install gh`
- A GitHub Personal Access Token (PAT) with `repo` scope.

### Steps

1. **Authenticate with GitHub CLI**
   Run the following command and paste your PAT when prompted, or use the token directly:
   ```bash
   echo "YOUR_GITHUB_PAT" | gh auth login --with-token
   ```

2. **Add or Update a Secret**
   Use the `gh secret set` command:
   ```bash
   gh secret set SECRET_NAME --body "secret_value" --repo AveryKing/phantom-apollo
   ```

3. **Verify Secrets (Optional)**
   You can list the names of current secrets to verify they were added:
   ```bash
   gh secret list --repo AveryKing/phantom-apollo
   ```

// turbo-all
### Automation Script
You can use the following snippet to batch add secrets from a `.env` file (be careful with which variables you include):
```bash
# Example: Adding Langfuse secrets
gh secret set LANGFUSE_PUBLIC_KEY --body "YOUR_VALUE" --repo AveryKing/phantom-apollo
gh secret set LANGFUSE_SECRET_KEY --body "YOUR_VALUE" --repo AveryKing/phantom-apollo
gh secret set LANGFUSE_HOST --body "https://us.cloud.langfuse.com" --repo AveryKing/phantom-apollo
```
