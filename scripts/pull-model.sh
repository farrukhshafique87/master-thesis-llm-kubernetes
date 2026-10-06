#!/usr/bin/env bash
# Pull the model into the Ollama PVC and warm it up. Usage: pull-model.sh <namespace>
set -euo pipefail
NS="${1:?usage: pull-model.sh <namespace>}"
MODEL="${OLLAMA_MODEL:-qwen2.5:0.5b}"

kubectl -n "$NS" rollout status deploy/ollama --timeout=300s
kubectl -n "$NS" exec deploy/ollama -- ollama pull "$MODEL"
# Warm-up: load model into memory (keep_alive is -1) so runs start "hot".
kubectl -n "$NS" exec deploy/ollama -- ollama run "$MODEL" "Say OK." >/dev/null
kubectl -n "$NS" exec deploy/ollama -- ollama list
