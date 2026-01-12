---
description: A collaborative session where the User acts as the "Driver" (on Discord) and the Agent acts as the "Navigator" (monitoring logs).
---

# Collaborative Verification Session

This workflow turns us into a debugging team: You play the User, I play the Sysadmin.

## Roles
- **User (Driver)**: Interacts with the live bot on Discord (e.g., `/hunt`).
- **Agent (Navigator)**: Watches `gcloud` logs in real-time and reports back status, errors, and internal thoughts.

## The Protocol

1.  **Initiate**: User says "Start debug session".
2.  **Baseline**: Agent checks `gcloud run services list` to confirm the revision is live.
3.  **Action**: User triggers a command in Discord (e.g., `/hunt`).
4.  **Confirm**: User tells Agent "Command sent".
5.  **Trace**: Agent immediately runs:
    ```bash
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=phantom-apollo" --limit 20 --order desc
    ```
6.  **Analysis**:
    - **HTTP 200?** -> Networking is good.
    - **"Thinking..." Stuck?** -> Async logic or Token failure.
    - **Error Log?** -> Agent analyzes stack trace and suggests a fix.
7.  **Iterate**: We repeat until the User sees the desired output in Discord.
