#!/bin/bash
export PROJECT_ID="gen-lang-client-0175387292"
export POOL_NAME="github-pool"
export PROVIDER_NAME="github-provider-condition" # New name

echo "🔍 Attempting Fix with Explicit Condition..."

# 1. Create Provider with explicit condition
# We map 'google.subject' -> 'assertion.sub'
# And we ADD a condition that checks 'assertion.repository' exists
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool=$POOL_NAME \
    --display-name="GitHub Actions Provider Condition" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --attribute-condition="assertion.repository_owner=='AveryKing'"

if [ $? -eq 0 ]; then
    echo "✅ Provider created successfully!"
    
    # Get Full Name
    PROVIDER_FULL_NAME=$(gcloud iam workload-identity-pools providers describe $PROVIDER_NAME \
        --project="${PROJECT_ID}" --location="global" \
        --workload-identity-pool=$POOL_NAME \
        --format="value(name)")
        
    echo "NEW PROVIDER STRING: $PROVIDER_FULL_NAME"
else
    echo "❌ Still failed. Let's try minimal mapping without condition next."
fi
