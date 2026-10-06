#!/usr/bin/env bash
# Scale an environment back to 1 replica per Deployment. Usage: resume-env.sh <namespace>
set -euo pipefail
NS="${1:?usage: resume-env.sh <namespace>}"
kubectl -n "$NS" scale deploy --all --replicas=1
kubectl -n "$NS" rollout status deploy/ollama --timeout=300s
kubectl -n "$NS" rollout status deploy/fastapi --timeout=300s
