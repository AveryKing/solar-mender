#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
SERVICE_NAME="solar-mender"
REPOSITORY="solar-mender-repo"
QUEUE_NAME="repair-jobs-queue"

echo "🚀 Starting deployment for project: $PROJECT_ID"

# 1. Enable APIs
echo "✅ Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudtasks.googleapis.com \
    aiplatform.googleapis.com

# 2. Create Artifact Registry Repository
echo "📦 Creating Artifact Registry..."
gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for CI/CD Repair Agent" || true

# 3. Create Cloud Tasks Queue
echo "⏳ Creating Cloud Tasks Queue..."
gcloud tasks queues create $QUEUE_NAME --location=$REGION || true

# 4. Build and Push Image
echo "🏗️ Building and pushing Docker image..."
IMAGE_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:latest"
gcloud builds submit --tag $IMAGE_URL

# 5. Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_URL \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION,DATABASE_URL=sqlite+aiosqlite:///./local.db,GITHUB_SECRET=placeholder,GITHUB_TOKEN=placeholder"

echo "🎉 Deployment complete!"
echo "📍 Service URL: $(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')"
