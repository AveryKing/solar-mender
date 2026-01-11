# 🛠️ Comprehensive Deployment Guide: CI/CD Repair Agent

This guide walk you through the end-to-end process of setting up the **Diviora Systems CI/CD Repair Agent**. This system uses FastAPI for webhooks, Google Cloud Tasks for queueing, and Google Vertex AI for self-healing logic.

---

## 📋 Prerequisites
Before you begin, ensure you have:
1.  **A Google Cloud Project** with billing enabled.
2.  **Google Cloud SDK (gcloud CLI)** installed and authenticated: `gcloud auth login`.
3.  **GitHub Repository** where you want to install the repair agent.
4.  **Python 3.11+** installed locally for testing.

---

## 1️⃣ Phase 1: Google Cloud Infrastructure
We will use a combination of automated scripts and manual verification.

### A. Run the Setup Script
The script `scripts/setup_gcp.sh` is designed to be idempotent. It handles API enablement and resource creation.
```bash
chmod +x scripts/setup_gcp.sh
./scripts/setup_gcp.sh
```
**What this does:**
*   Enables `run.googleapis.com`, `cloudtasks.googleapis.com`, `aiplatform.googleapis.com`, and `artifactregistry.googleapis.com`.
*   Creates an Artifact Registry repo named `solar-mender-repo`.
*   Creates a Cloud Tasks queue named `repair-jobs-queue`.
*   Deploys a "placeholder" version of the app to get your **Service URL**.

### B. Note the Service URL
After the script finishes, it will print a `Service URL`. It looks like:
`https://solar-mender-xyz-uc.a.run.app`
**You will need this for the GitHub Webhook.**

---

## 2️⃣ Phase 2: GitHub Integration

### A. Create a Fine-Grained Personal Access Token (PAT)
1.  Go to **GitHub Settings > Developer settings > Personal access tokens > Fine-grained tokens**.
2.  Click **Generate new token**.
3.  **Token Name**: `Diviora-Repair-Agent-Token`
4.  **Repository access**: Select **Only select repositories** and pick your target repo.
5.  **Permissions**:
    *   `Actions`: Read (to fetch build logs)
    *   `Contents`: Read & Write (to fetch code and commit fixes)
    *   `Metadata`: Read (auto-selected)
    *   `Pull requests`: Read & Write (to open and comment on PRs)
    *   `Workflows`: Read (to see workflow status)
6.  **Generate** and copy the token. **This is your `GITHUB_TOKEN`**.

### B. Create a Webhook Secret
Create a secure random string. You can use this command:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
**This is your `GITHUB_SECRET`**.

### C. Configure the Repository Webhook
1.  In your GitHub Repo, go to **Settings > Webhooks > Add webhook**.
2.  **Payload URL**: `<YOUR_SERVICE_URL>/api/v1/webhook/github`
3.  **Content type**: `application/json`
4.  **Secret**: Paste your `GITHUB_SECRET`.
5.  **Which events?**: Select **Let me select individual events** and check:
    *   ✅ Workflow runs
6.  **Add webhook**.

---

## 3️⃣ Phase 3: Secure CI/CD with Workload Identity Federation (WIF)
To avoid using insecure service account keys, we use WIF.

### A. Provision WIF Resources
Run these commands, replacing variables as needed:
```bash
export PROJECT_ID="your-project-id"
export REPO_NAME="org/your-repo" # e.g., "diviora/solar-mender"

# 1. Create Pool
gcloud iam workload-identity-pools create "github-pool" \
    --project="${PROJECT_ID}" --location="global" \
    --display-name="GitHub Actions Pool"

# 2. Create Provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="${PROJECT_ID}" --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Actions Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository"

# 3. Create Service Account for GitHub Actions
gcloud iam service-accounts create "github-actions-sa" \
    --project="${PROJECT_ID}" --display-name="GitHub Actions SA"

# 4. Grant Roles to the Service Account
# Artifact Registry
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"
# Cloud Run
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"
# IAM to pass roles
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# 5. Connect Provider to Service Account
gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$(gcloud projects list --filter="projectId=${PROJECT_ID}" --format="value(projectNumber)")/locations/global/workloadIdentityPools/github-pool/attribute.repository/${REPO_NAME}"
```

---

## 4️⃣ Phase 4: Configure GitHub Secrets
Navigate to your repository **Settings > Secrets and variables > Actions** and add:

| Name | Value |
| :--- | :--- |
| `GCP_PROJECT_ID` | `your-project-id` |
| `GCP_WIF_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_WIF_SERVICE_ACCOUNT` | `github-actions-sa@your-project-id.iam.gserviceaccount.com` |
| `GITHUB_TOKEN` | The PAT from Phase 2A |
| `GITHUB_SECRET` | The Secret from Phase 2B |
| `SERVICE_URL` | Your Cloud Run Service URL |
| `DATABASE_URL` | For production, use a Cloud SQL PostgreSQL URL. For testing, you can use a Persistent Disk or temporary SQLite. |
| `CLOUD_TASKS_QUEUE` | `repair-jobs-queue` |

---

## 🔍 Troubleshooting & Monitoring

### 1. Webhook 403 Forbidden
*   **Cause**: The HMAC signature verification failed.
*   **Fix**: Ensure the `GITHUB_SECRET` in your GitHub Webhook settings matches exactly the `GITHUB_SECRET` in your Cloud Run environment variables.

### 2. Cloud Tasks Failures
*   **Cause**: The service account running your app doesn't have `roles/cloudtasks.enqueuer`.
*   **Fix**: Grant the `Cloud Tasks Enqueuer` role to the default compute service account of your project.

### 3. Infinite Loops
*   **Cause**: The agent is fixing its own failures.
*   **Fix**: We have code to prevent this, but check that the GitHub token you use is linked to a user/bot named `repair-agent` as per the logic in `agent/nodes/diagnose.py`.

### 4. Vertex AI 403 Permission Denied
*   **Cause**: Vertex AI API not enabled or lack of `roles/aiplatform.user`.
*   **Fix**: Enable AI Platform in the console and ensure the Cloud Run service account has permission.

### 5. Viewing Logs
To see what the agent is thinking:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=solar-mender" --limit 20
```
