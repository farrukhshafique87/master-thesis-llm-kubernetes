#!/usr/bin/env bash
# Start an environment again. Usage: resume-env.sh <overlay-dir> <namespace>
# Re-applies the overlay (restores Ingress and replicas) and waits for the pods.
set -euo pipefail
OVERLAY="${1:?usage: resume-env.sh <overlay-dir> <namespace>}"
NS="${2:?usage: resume-env.sh <overlay-dir> <namespace>}"

kubectl apply -k "$OVERLAY"
kubectl -n "$NS" scale deploy --all --replicas=1
kubectl -n "$NS" rollout status deploy/ollama --timeout=300s
kubectl -n "$NS" rollout status deploy/fastapi --timeout=300s
if kubectl -n "$NS" get deploy gateway >/dev/null 2>&1; then
  kubectl -n "$NS" rollout status deploy/gateway --timeout=300s
fi
