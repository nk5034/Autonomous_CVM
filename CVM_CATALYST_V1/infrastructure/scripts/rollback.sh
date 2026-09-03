#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <environment> <release_name> [revision]"
  exit 1
fi

ENVIRONMENT_RAW="$1"
RELEASE_NAME="$2"
REQUESTED_REVISION="${3:-}"
ENVIRONMENT="${ENVIRONMENT_RAW,,}"
NAMESPACE="cvm-catalyst-$ENVIRONMENT"

if [[ "$ENVIRONMENT" == "prod" ]]; then
  NAMESPACE="cvm-catalyst-prod"
fi

if [[ -z "$REQUESTED_REVISION" ]]; then
  REVISION="$(helm history "$RELEASE_NAME" -n "$NAMESPACE" | awk 'NR > 1 {print $1}' | tail -n 2 | head -n 1)"
else
  REVISION="$REQUESTED_REVISION"
fi

if [[ -z "$REVISION" ]]; then
  echo "Unable to determine rollback revision for release $RELEASE_NAME in $NAMESPACE"
  exit 1
fi

echo "Rolling back $RELEASE_NAME in $NAMESPACE to revision $REVISION"
helm rollback "$RELEASE_NAME" "$REVISION" -n "$NAMESPACE" --wait --timeout 10m

kubectl rollout status deployment/cvm-catalyst-backend -n "$NAMESPACE" --timeout=5m
kubectl rollout status deployment/cvm-catalyst-frontend -n "$NAMESPACE" --timeout=5m

echo "Rollback completed successfully"
