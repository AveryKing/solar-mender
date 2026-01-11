# Deployment Workflow

1.  **Code Change**: Agent makes changes (code, config, infrastructure).
2.  **Commit**: Agent commits changes with a descriptive message.
3.  **Push**: Agent pushes to `main`.
4.  **Monitor**: Agent uses `gh run watch` or checks Cloud Run logs via `gcloud` to monitor progress.
5.  **Diagnose**: If failure, Agent reads logs (`gcloud logging read ...`).
6.  **Fix**: Agent applies fix and repeats from Step 2.
7.  **Verify**: Agent confirms successful deployment.

**Tools Used:**
- `git`: For version control.
- `gh`: GitHub CLI for monitoring Actions.
- `gcloud`: Google Cloud CLI for logs and Cloud Run status.
