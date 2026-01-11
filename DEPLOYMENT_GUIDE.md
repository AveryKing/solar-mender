# Configuration & Deployment Guide: CI/CD Repair Agent

This guide provides step-by-step instructions to configure, authenticate, and deploy the Diviora Systems CI/CD Repair Agent.

---

## 1. GitHub Configuration

### A. Create a Personal Access Token (PAT)
The agent needs a token to read logs, fetch code, and open Pull Requests.
1.  Go to **GitHub Settings > Developer settings > Personal access tokens > Fine-grained tokens**.
2.  Click **Generate new token**.
3.  **Permissions**:
    *   **Repository permissions**:
        *   `Contents`: Read and write (to fix code and create branches).
        *   `Pull requests`: Read and write (to open PRs).
        *   `Workflows`: Read (to see run status).
        *   `Actions`: Read (to fetch logs).
4.  Copy the token as `GITHUB_TOKEN`.

### B. Configure GitHub Webhook
1.  Go to your Repository **Settings > Webhooks > Add webhook**.
2.  **Payload URL**: `https://<your-cloud-run-url>/api/v1/webhook/github`
    *   *Note: You will get this URL after running the setup script.*
3.  **Content type**: `application/json`
4.  **Secret**: Create a random strong string (e.g., `openssl rand -base64 32`). Copy this as `GITHUB_SECRET`.
5.  **Events**: Select **Let me select individual events** and check **Workflow runs**.

---

## 2. Google Cloud Platform (GCP) Setup

### A. Initial Provisioning
Run the provided setup script to enable APIs and create the necessary infrastructure:
```bash
./scripts/setup_gcp.sh
```

### B. Vertex AI
Ensure your project has the **Vertex AI User** role enabled for the service account running Cloud Run (usually the `Default Compute Service Account` or a custom one).

### C. Cloud Tasks
The setup script creates a queue named `repair-jobs-queue`. If you want to use a different name, update it in `app/core/config.py`.

---

## 3. GitHub Actions CI/CD (Production)

We use **Workload Identity Federation** to avoid storing long-lived GCP keys.

### A. Setup WIF (One-time)
Run these commands in your terminal to allow GitHub to talk to GCP:
```bash
# 1. Create a Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" --location="global"

# 2. Create a Workload Identity Provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --location="global" --workload-identity-pool="github-pool" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository"

# 3. Allow GitHub to impersonate your Service Account
gcloud iam service-accounts add-iam-policy-binding "YOUR_SERVICE_ACCOUNT_EMAIL" \
    --project="YOUR_PROJECT_ID" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_ORG/YOUR_REPO"
```

### B. GitHub Secrets
Add the following to **Settings > Secrets and variables > Actions**:

| Secret Name | Description |
| :--- | :--- |
| `GCP_PROJECT_ID` | Your Google Cloud Project ID |
| `GCP_WIF_PROVIDER` | `projects/NUM/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_WIF_SERVICE_ACCOUNT` | The email of the service account created in Step 3A |
| `GITHUB_TOKEN` | The PAT created in Step 1A |
| `GITHUB_SECRET` | The Webhook Secret created in Step 1B |
| `SERVICE_URL` | The URL of your Cloud Run service |
| `DATABASE_URL` | Connection string (e.g., `postgresql+asyncpg://...`) |

---

## 4. Local Development

1.  Copy `env.example` to `.env`.
2.  Fill in the values. For local DB, use:
    `DATABASE_URL=sqlite+aiosqlite:///./local.db`
3.  Install dependencies: `make install`
4.  Run the app: `make dev`
5.  Use `ngrok` to tunnel the webhook to your local machine:
    `ngrok http 8080`
    *Update your GitHub Webhook URL to the ngrok URL for testing.*
