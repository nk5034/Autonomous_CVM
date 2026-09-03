#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <environment> <image_tag> [release_name]"
  exit 1
fi

ENVIRONMENT_RAW="$1"
IMAGE_TAG="$2"
RELEASE_NAME="${3:-cvm-catalyst}"
ENVIRONMENT="${ENVIRONMENT_RAW,,}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHART_DIR="$ROOT_DIR/infrastructure/helm/cvm-catalyst"
VALUES_FILE="$CHART_DIR/values-$ENVIRONMENT.yaml"

if [[ ! -f "$VALUES_FILE" ]]; then
  echo "Environment values file not found: $VALUES_FILE"
  exit 1
fi

NAMESPACE="cvm-catalyst-$ENVIRONMENT"
if [[ "$ENVIRONMENT" == "prod" ]]; then
  NAMESPACE="cvm-catalyst-prod"
fi

echo "Deploying release $RELEASE_NAME to $NAMESPACE with tag $IMAGE_TAG"

helm upgrade --install "$RELEASE_NAME" "$CHART_DIR" \
  --namespace "$NAMESPACE" \
  --create-namespace \
  -f "$CHART_DIR/values.yaml" \
  -f "$VALUES_FILE" \
  --set images.backend.tag="$IMAGE_TAG" \
  --set images.frontend.tag="$IMAGE_TAG" \
  --wait \
  --timeout 10m

kubectl rollout status deployment/cvm-catalyst-backend -n "$NAMESPACE" --timeout=5m
kubectl rollout status deployment/cvm-catalyst-frontend -n "$NAMESPACE" --timeout=5m

echo "Deployment completed successfully for $ENVIRONMENT_RAW"
