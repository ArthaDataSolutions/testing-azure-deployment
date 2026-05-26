#!/usr/bin/env bash
# Build the image, push to Azure Container Registry, and create/update the
# Azure Container Apps deployment. Idempotent: re-running updates in place.
set -euo pipefail

# ── Pre-filled defaults (override via env vars if needed) ─────────────────────
RESOURCE_GROUP="${RESOURCE_GROUP:-my-etl-rg}"
LOCATION="${LOCATION:-eastus}"
ACR_NAME="${ACR_NAME:-myacr}"
ACA_ENV="${ACA_ENV:-my-aca-env}"
APP_NAME="${APP_NAME:-migrated-etl-jobs}"

IMAGE_NAME="${IMAGE_NAME:-$APP_NAME}"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d%H%M%S)}"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"

echo ">> Logging in to ACR ${ACR_NAME}"
az acr login --name "$ACR_NAME"

echo ">> Building image ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"
az acr build \
  --registry "$ACR_NAME" \
  --image "${IMAGE_NAME}:${IMAGE_TAG}" \
  --file Dockerfile \
  .

echo ">> Ensuring resource group ${RESOURCE_GROUP} exists"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" >/dev/null

if ! az containerapp env show -g "$RESOURCE_GROUP" -n "$ACA_ENV" >/dev/null 2>&1; then
  echo ">> Creating Container Apps environment ${ACA_ENV}"
  az containerapp env create \
    --name "$ACA_ENV" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION"
fi

if az containerapp show -g "$RESOURCE_GROUP" -n "$APP_NAME" >/dev/null 2>&1; then
  echo ">> Updating container app ${APP_NAME}"
  az containerapp update \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --image "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"
else
  echo ">> Creating container app ${APP_NAME}"
  ACR_PASSWORD="$(az acr credential show -n "$ACR_NAME" --query 'passwords[0].value' -o tsv)"
  ACR_USER="$(az acr credential show -n "$ACR_NAME" --query 'username' -o tsv)"
  az containerapp create \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --environment "$ACA_ENV" \
    --image "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}" \
    --registry-server "$ACR_LOGIN_SERVER" \
    --registry-username "$ACR_USER" \
    --registry-password "$ACR_PASSWORD" \
    --min-replicas 0 \
    --max-replicas 1 \
    --cpu 0.5 \
    --memory 1.0Gi
fi

echo ">> Deployment complete. Image: ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"
