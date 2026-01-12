---
description: Configure MCP Servers in the Global Antigravity Directory
---
# MCP Server Configuration Workflow

This workflow guides you through configuring Model Context Protocol (MCP) servers in the global Antigravity directory. This is the **source of truth** for all MCP tools available to the IDE.

**Global Config Path**: `/Users/avery/.gemini/antigravity/mcp_config.json`

---

## Execution Steps

// turbo-all
1.  **Read Current Configuration**:
    *   Since the file is outside the workspace, use `cat` to read it:
        ```bash
        cat /Users/avery/.gemini/antigravity/mcp_config.json
        ```

2.  **Backup Configuration**:
    *   Create a backup before editing:
        ```bash
        cp /Users/avery/.gemini/antigravity/mcp_config.json /Users/avery/.gemini/antigravity/mcp_config.backup.json
        ```

3.  **Construct Server Entry**:
    *   **NPM-based Servers**:
        ```json
        "server-name": {
          "command": "npx",
          "args": ["-y", "@org/package@latest"],
          "env": { "API_KEY": "..." }
        }
        ```
    *   **Remote Servers (via mcp-remote)**:
        ```json
        "server-name": {
          "command": "npx",
          "args": [
            "mcp-remote",
            "https://api.example.com/mcp", // Remote URL
            "--header", "Authorization: Bearer ..."
          ]
        }
        ```

4.  **Update Configuration**:
    *   Use `jq` or a temporary Node script to update the JSON safely.
    *   **WARNING**: Do not use `write_to_file` directly on global files if simpler tools fail.

5.  **Restart Session**:
    *   After updating `mcp_config.json`, you must **restart your IDE/Agent session** for changes to take effect.

---

## Example: Adding a POSTGRES Server

```bash
# 1. Read
cat /Users/avery/.gemini/antigravity/mcp_config.json

# 2. Update (Conceptually)
# {
#   "mcpServers": {
#     "postgres": {
#       "command": "npx",
#       "args": ["-y", "@mcp/postgres", "postgresql://user:pass@localhost:5432/db"]
#     }
#   }
# }
```
