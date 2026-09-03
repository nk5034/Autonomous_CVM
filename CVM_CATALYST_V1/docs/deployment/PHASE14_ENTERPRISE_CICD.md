# Phase 14 Enterprise CI/CD

## Overview

Phase 14 introduces an enterprise CI/CD implementation for CVM Catalyst with:

- GitHub Actions for CI, image build/publish, deployment, promotion, and rollback.
- Docker images for backend and frontend.
- Kubernetes manifests (base + environment overlays).
- Helm chart with environment-specific values files.
- Promotion policy from DEV -> QA -> UAT -> PROD.
- Automated rollback via Helm revision history.

## Pipeline Components

### GitHub Actions

- `.github/workflows/ci.yml`
  - Backend checks in workspace virtual environment (`.venv`): Ruff, MyPy, unit tests.
  - Frontend checks: lint, type-check, test, build.

- `.github/workflows/build-images.yml`
  - Builds and pushes backend/frontend images to GHCR.
  - Tags images with commit SHA and `latest` on default branch.

- `.github/workflows/deploy.yml`
  - Deploys a selected image tag into DEV, QA, UAT, or PROD.
  - Uses Helm for deployment automation.

- `.github/workflows/promote.yml`
  - Enforces promotion sequence using `promotion_guard.py`.
  - Calls reusable deploy workflow for the target environment.

- `.github/workflows/rollback.yml`
  - Performs Helm rollback to a selected or previous revision.

### Deployment Scripts

- `infrastructure/scripts/promotion_guard.py`
  - Validates target environments and promotion transitions.

- `infrastructure/scripts/deploy.sh`
  - Executes Helm upgrade/install with environment values and image tag.

- `infrastructure/scripts/rollback.sh`
  - Rolls back Helm release and verifies rollout health.

### Kubernetes

- `infrastructure/kubernetes/base`
  - Base resources: configmap, backend/frontend deployments and services, ingress.

- `infrastructure/kubernetes/overlays/{dev,qa,uat,prod}`
  - Environment-specific replica counts, ingress hosts, and image tags.

### Helm

- `infrastructure/helm/cvm-catalyst`
  - Application chart and templates.
  - Values files:
    - `values.yaml` (common)
    - `values-dev.yaml`
    - `values-qa.yaml`
    - `values-uat.yaml`
    - `values-prod.yaml`

## Required Repository Secrets

Create these secrets in GitHub repository settings:

- `KUBECONFIG_DEV`
- `KUBECONFIG_QA`
- `KUBECONFIG_UAT`
- `KUBECONFIG_PROD`

Each value should be a kubeconfig content block for the corresponding cluster.

## Required GitHub Environments

Create these environments in GitHub:

- `DEV`
- `QA`
- `UAT`
- `PROD`

Recommended protection rules:

- DEV: minimal restrictions.
- QA/UAT: required reviewer approval.
- PROD: required approvals and deployment branch restrictions.

## Promotion Model

Valid promotions are:

1. DEV -> QA
2. QA -> UAT
3. UAT -> PROD

Any skipped stage is rejected by automation.

## Local Operations (Workspace .venv)

From repository root:

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe infrastructure\scripts\promotion_guard.py validate-transition --source DEV --target QA
```

### Bash

```bash
./.venv/bin/python infrastructure/scripts/promotion_guard.py validate-transition --source DEV --target QA
```

## Deployment Operations

Deploy via GitHub Actions:

1. Run `Build And Publish Images`.
2. Capture the generated image SHA tag.
3. Run `Deploy` with:
   - `environment`: DEV, QA, UAT, or PROD
   - `image_tag`: the SHA tag

## Rollback Operations

Rollback via GitHub Actions:

1. Run `Rollback`.
2. Select `environment` and `release_name`.
3. Optional: provide `revision`.
4. If omitted, the script selects the previous revision.

## Notes

- Replace `REPLACE_ME` image repository placeholders in Kubernetes and Helm values.
- Store application secrets (`DATABASE_URL`, API keys) via Helm values in secure secret management workflows.
- Integrate policy checks (SAST, container scanning, IaC scanning) in a follow-up hardening phase if required.
