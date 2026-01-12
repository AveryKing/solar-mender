#!/bin/bash
export PROJECT_ID="gen-lang-client-0175387292"
export POOL_NAME="github-pool"
export PROVIDER_NAME="github-short" 

echo "🔍 Attempting Fix with Short Name & Condition..."

# 1. Create Provider
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool=$POOL_NAME \
    --display-name="GitHub Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
    --attribute-condition="assertion.repository_owner=='AveryKing'"

if [ $? -eq 0 ]; then
    echo "✅ Provider created successfully!"
    
    # Get Full Name
    PROVIDER_FULL_NAME=$(gcloud iam workload-identity-pools providers describe $PROVIDER_NAME \
        --project="${PROJECT_ID}" --location="global" \
        --workload-identity-pool=$POOL_NAME \
        --format="value(name)")
        
    echo "NEW PROVIDER STRING: $PROVIDER_FULL_NAME"
    
    # Bind IAM (Since we have a new provider name, we might need to re-bind or ensure the SA is ready)
    PROJECT_NUMBER=$(gcloud projects list --filter="projectId=${PROJECT_ID}" --format="value(projectNumber)")
    gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/AveryKing/solar-mender" --quiet

else
    echo "❌ Failed."
fi
