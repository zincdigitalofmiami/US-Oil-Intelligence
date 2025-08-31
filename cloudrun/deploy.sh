#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID=${PROJECT_ID:-""}
REGION=${REGION:-"us-central1"}
SERVICE=${SERVICE:-"soy-intel-api"}
[[ -z "$PROJECT_ID" ]] && echo "Set PROJECT_ID" && exit 1
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com --project $PROJECT_ID || true
gcloud artifacts repositories create containers --repository-format=docker --location=$REGION --project $PROJECT_ID || true
gcloud builds submit . --tag $REGION-docker.pkg.dev/$PROJECT_ID/containers/$SERVICE:latest --project $PROJECT_ID
gcloud run deploy $SERVICE --image $REGION-docker.pkg.dev/$PROJECT_ID/containers/$SERVICE:latest   --region $REGION --allow-unauthenticated --project $PROJECT_ID --set-env-vars API_PORT=8080
