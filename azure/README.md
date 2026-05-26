# Azure Container Apps deploy

This directory packages the generated Boomi-to-Python project for **Azure
Container Apps (ACA)**. The Dockerfile builds an image that runs
`python runtime.py` once per invocation, which is a good fit for ACA's
scale-to-zero job execution.

## Files

| File             | Purpose                                                  |
|------------------|----------------------------------------------------------|
| `Dockerfile`     | Multi-stage Python 3.12 image with native deps for `lxml`, `psycopg`, `paramiko` |
| `.dockerignore`  | Keeps the build context small                            |
| `aca-app.yaml`   | Declarative Container Apps template (`az containerapp ... --yaml`) |
| `deploy.sh`      | One-shot build + push + create-or-update script          |

## Required environment

Set these before running `bash azure/deploy.sh`:

```bash
export RESOURCE_GROUP=my-etl-rg
export LOCATION=eastus
export ACR_NAME=myacr             # without .azurecr.io
export ACA_ENV=my-aca-env
export APP_NAME=migrated-boomi-jobs
# Optional:
# export IMAGE_NAME=migrated-boomi-jobs
# export IMAGE_TAG=v1
```

The connector and process-property secrets your migrated jobs read from
environment variables (see the project root's `.env.example`) must be set on
the container app itself — either with `az containerapp update --set-env-vars`
or by adding `secrets` and `env` entries to `aca-app.yaml`.

## Deploy

```bash
bash azure/deploy.sh
```

Re-runs are idempotent: the script will create the resource group, ACR
environment, and container app on first run, then update the image on each
subsequent run.
