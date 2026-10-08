#!/usr/bin/env bash
# Pull the model into the Ollama PVC and load it into memory.
# Usage: pull-model.sh <namespace> [overlay-dir]
# With an overlay directory, NetworkPolicies are lifted for the download (they
# block the registry) and re-applied afterwards.
set -euo pipefail
NS="${1:?usage: pull-model.sh <namespace> [overlay-dir]}"
OVERLAY="${2:-}"
MODEL="${OLLAMA_MODEL:-qwen2.5:0.5b}"

kubectl -n "$NS" rollout status deploy/ollama --timeout=300s

if [ -n "$OVERLAY" ]; then
  kubectl -n "$NS" delete networkpolicy --all --ignore-not-found
fi

kubectl -n "$NS" exec deploy/ollama -c ollama -- ollama pull "$MODEL"
# Load the model (keep-alive is -1, so it stays in memory).
kubectl -n "$NS" exec deploy/ollama -c ollama -- ollama run "$MODEL" "Say OK." >/dev/null
kubectl -n "$NS" exec deploy/ollama -c ollama -- ollama list

if [ -n "$OVERLAY" ]; then
  kubectl apply -k "$OVERLAY"
fi
