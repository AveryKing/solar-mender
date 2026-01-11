#!/bin/bash

# ==============================================================================
# Phase 3: Workload Identity Federation (WIF) Setup - GUARANTEED FIX
# ------------------------------------------------------------------------------
# Repo: AveryKing/solar-mender
# ==============================================================================

export PROJECT_ID="gen-lang-client-0175387292"
export REPO_NAME="AveryKing/solar-mender"

echo "🚀 Starting GUARANTEED WIF setup for project: $PROJECT_ID"

# 1. Get Project Number
PROJECT_NUMBER=$(gcloud projects list --filter="projectId=${PROJECT_ID}" --format="value(projectNumber)")
echo "🔢 Project Number: ${PROJECT_NUMBER}"

# 2. Pool Check/Create
gcloud iam workload-identity-pools describe "github-pool" --project="${PROJECT_ID}" --location="global" &>/dev/null
if [ $? -ne 0 ]; then
    echo "📟 Creating Pool..."
    gcloud iam workload-identity-pools create "github-pool" --project="${PROJECT_ID}" --location="global" --display-name="GitHub Actions Pool"
else
    echo "✅ Pool exists."
fi

# 3. Delete existing Provider to clear the "attribute condition" error
echo "📡 Force-deleting existing provider to clear stale configurations..."
gcloud iam workload-identity-pools providers delete "github-provider" \
    --project="${PROJECT_ID}" --location="global" --workload-identity-pool="github-pool" --quiet || true

echo "⏳ Waiting for deletion to propagate (10s)..."
sleep 10

# 4. Create fresh Provider with standard mapping
echo "📡 Creating fresh Workload Identity Provider..."
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Actions Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# 5. Service Account Check/Create
gcloud iam service-accounts describe "github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" --project="${PROJECT_ID}" &>/dev/null
if [ $? -ne 0 ]; then
    echo "👤 Creating Service Account..."
    gcloud iam service-accounts create "github-actions-sa" --project="${PROJECT_ID}" --display-name="GitHub Actions SA"
else
    echo "✅ Service Account exists."
fi

# 6. Assign Roles
echo "🔑 Refreshing roles..."
for ROLE in "roles/artifactregistry.writer" "roles/run.admin" "roles/iam.serviceAccountUser"; do
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="${ROLE}" --quiet >/dev/null
done

# 7. Bind Repository
echo "🤝 Binding Repository..."
gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${REPO_NAME}" --quiet

echo "----------------------------------------------------------------"
echo "🎉 DEPLOYMENT READY!"
echo "----------------------------------------------------------------"
echo "GCP_PROJECT_ID: $PROJECT_ID"
echo "GCP_WIF_PROVIDER: projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
echo "GCP_WIF_SERVICE_ACCOUNT: github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com"
echo "----------------------------------------------------------------"
