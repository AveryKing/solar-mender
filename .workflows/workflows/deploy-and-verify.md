---
description: Deploy changes to production and then immediately transition into a verification session.
---

# Deploy and Verify Workflow

// turbo-all

This workflow automates the path from "Code Fixed" to "Verified in Production".

## Execution Steps

1. **Commit and Push Changes**:
   - Stage all changes: `git add .`
   - Commit: `git commit -m "<message>"`
   - Push: `git push origin main`

2. **Wait for Deployment**:
   - The GitHub Action takes approximately 2-3 minutes to build and deploy.
   - We will monitor the Cloud Run service status to detect when the new revision is live.
   - Command to monitor:
     ```bash
     current_rev=$(gcloud run services describe phantom-apollo --region us-central1 --format="value(status.latestReadyRevisionName)")
     echo "Current Revision: $current_rev"
     echo "Waiting for new revision..."
     
     while true; do
       new_rev=$(gcloud run services describe phantom-apollo --region us-central1 --format="value(status.latestReadyRevisionName)")
       if [ "$new_rev" != "$current_rev" ]; then
         echo "✅ New revision detected: $new_rev"
         break
       fi
       echo "Still waiting... (checking again in 10s)"
       sleep 10
     done
     ```

3. **Verify Deployment Health**:
   - Check if the new revision is receiving traffic.
   - `gcloud run services describe phantom-apollo --region us-central1 --format="value(status.traffic)"`

4. **Start Verification Session**:
   - Once the new revision is live, immediately switch to the verification protocol.
   - **Action**: User opens Discord.
   - **Navigator**: Agent starts tailing logs.

## Usage
Run this when you have applied a fix (like the JSON parsing patch) and want to test it in the real world immediately.
