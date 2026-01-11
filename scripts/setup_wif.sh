#!/bin/bash

# ==============================================================================
# Phase 3: Workload Identity Federation (WIF) Setup
# ------------------------------------------------------------------------------
# This script configures GCP to allow GitHub Actions to deploy without keys.
# Repo: AveryKing/solar-mender
# ==============================================================================

# 1. SET YOUR PROJECT ID HERE
# You can find this by running: gcloud config get-value project
export PROJECT_ID="YOUR_PROJECT_ID_HERE"
export REPO_NAME="AveryKing/solar-mender"

if [ "$PROJECT_ID" == "YOUR_PROJECT_ID_HERE" ]; then
    echo "❌ ERROR: Please edit this script and set your PROJECT_ID on line 11."
    exit 1
fi

echo "🚀 Starting WIF setup for project: $PROJECT_ID"

# 2. Create a Workload Identity Pool
echo "📟 Creating Workload Identity Pool..."
gcloud iam workload-identity-pools create "github-pool" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --display-name="GitHub Actions Pool" || true

# 3. Create a Workload Identity Provider
echo "📡 Creating Workload Identity Provider..."
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Actions Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" || true

# 4. Create the Service Account
echo "👤 Creating Service Account: github-actions-sa"
gcloud iam service-accounts create "github-actions-sa" \
    --project="${PROJECT_ID}" \
    --display-name="GitHub Actions SA" || true

# 5. Assign Roles to the Service Account
echo "🔑 Assigning roles..."

# Artifact Registry (to push images)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Cloud Run Admin (to deploy)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Service Account User (to act as the runtime SA)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# 6. Bind GitHub Repository to the Service Account
echo "🤝 Binding GitHub Repository to Service Account..."
PROJECT_NUMBER=$(gcloud projects list --filter="projectId=${PROJECT_ID}" --format="value(projectNumber)")

gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${REPO_NAME}"

echo "----------------------------------------------------------------"
echo "✅ SUCCESS! Use these values in your GitHub Secrets:"
echo "----------------------------------------------------------------"
echo "GCP_PROJECT_ID: $PROJECT_ID"
echo "GCP_WIF_PROVIDER: projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
echo "GCP_WIF_SERVICE_ACCOUNT: github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com"
echo "----------------------------------------------------------------"
