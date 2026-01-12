---
description: Monitor GitHub Action status and fix errors until the deployment passes.
---

# Deploy and Fix Workflow

Use this workflow to monitor a GitHub Action run, analyze failures, and apply fixes until the build and deployment succeed.

## Steps:

1. **Check Status**:
   - Run `gh run list --limit 5` to see the latest workflow runs.
   - Identify the `ID` of the latest run or the specific run that failed.

2. **Diagnose Failure**:
   - If a run failed, get the logs using `gh run view <RUN_ID> --log`.
   - Analyze the logs to identify the root cause (e.g., missing environment variables, build errors, file path issues).

3. **Apply Fix**:
   - Fix the identified issues in the codebase or workflow configuration.
   - Stage, commit, and push the changes: `git add . && git commit -m "fix: [description]" && git push origin main`.

4. **Iterate**:
   - Return to Step 1 and repeat until the latest run shows `success`.

5. **Final Verification**:
   - Once successfully deployed, verify the live service (e.g., check Cloud Run URL or UI).
