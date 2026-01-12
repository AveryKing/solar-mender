#!/bin/bash

# ==============================================================================
# WIF DEBUG & FIX SCRIPT
# ------------------------------------------------------------------------------
# 1. Checks current state
# 2. Creates provider with simplified syntax
# 3. Verifies success
# ==============================================================================

export PROJECT_ID="gen-lang-client-0175387292"
export POOL_NAME="github-pool"
export PROVIDER_NAME="github-provider-fixed" # Using a new name to be safe

echo "🔍 Checking Project: $PROJECT_ID"

# 1. Check Pool
echo "----------------------------------------------------------------"
echo "Step 1: Checking Workload Identity Pool"
gcloud iam workload-identity-pools describe $POOL_NAME \
    --project="${PROJECT_ID}" --location="global" &>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️ Pool not found. Creating..."
    gcloud iam workload-identity-pools create $POOL_NAME \
        --project="${PROJECT_ID}" --location="global" \
        --display-name="GitHub Actions Pool"
else
    echo "✅ Pool exists."
fi

# 2. Create Provider (Minimal Mapping)
echo "----------------------------------------------------------------"
echo "Step 2: Creating Provider '$PROVIDER_NAME'"
# We strip the mapping down to the bare minimum first to pass validation
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool=$POOL_NAME \
    --display-name="GitHub Actions Provider Fixed" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"

if [ $? -eq 0 ]; then
    echo "✅ Provider created successfully!"
else
    echo "❌ Provider creation FAILED. Stop here."
    exit 1
fi

# 3. Get Full Provider Name
PROVIDER_FULL_NAME=$(gcloud iam workload-identity-pools providers describe $PROVIDER_NAME \
    --project="${PROJECT_ID}" --location="global" \
    --workload-identity-pool=$POOL_NAME \
    --format="value(name)")

# 4. Bind IAM Role
echo "----------------------------------------------------------------"
echo "Step 3: Binding IAM Role"
# We need to get the numeric project ID
PROJECT_NUMBER=$(gcloud projects list --filter="projectId=${PROJECT_ID}" --format="value(projectNumber)")
REPO_NAME="AveryKing/solar-mender"

# Bind to the specific repository attribute
gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/${REPO_NAME}"

echo "----------------------------------------------------------------"
echo "✅ FIXED! Update your GitHub Secret 'GCP_WIF_PROVIDER' to:"
echo "----------------------------------------------------------------"
echo "$PROVIDER_FULL_NAME"
echo "----------------------------------------------------------------"
