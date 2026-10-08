#!/usr/bin/env bash
# Measure one configuration: switch to it, then run the /chat and /health tests.
# Usage: measure-config.sh <config> <repetition>
# Configs: c0-baseline c1-rbac c2-netpol c4-tls c5-gateway c6-all
# Round-robin over configurations (interleaving), for example:
#   for r in 1 2 3; do for c in c0-baseline c1-rbac c2-netpol c4-tls c5-gateway c6-all; do
#     ./scripts/measure-config.sh "$c" "$r"; done; done
set -euo pipefail

CONFIG="${1:?usage: measure-config.sh <config> <repetition>}"
REP="${2:?usage: measure-config.sh <config> <repetition>}"
EXP="${EXP:-exp-06-final}"
MODEL="${OLLAMA_MODEL:-qwen2.5:0.5b}"

cd "$(dirname "$0")/.."

ALL_NS="llm-baseline llm-c1-rbac llm-c2-netpol llm-c4-tls llm-c5-gateway llm-secure"

case "$CONFIG" in
  c0-baseline) OVERLAY=kind-baseline;   NS=llm-baseline;   URL=http://localhost:8010;  AUTH=no  ;;
  c1-rbac)     OVERLAY=kind-c1-rbac;    NS=llm-c1-rbac;    URL=http://localhost:8010;  AUTH=no  ;;
  c2-netpol)   OVERLAY=kind-c2-netpol;  NS=llm-c2-netpol;  URL=http://localhost:8010;  AUTH=no  ;;
  c4-tls)      OVERLAY=kind-c4-tls;     NS=llm-c4-tls;     URL=https://localhost:8443; AUTH=no  ;;
  c5-gateway)  OVERLAY=kind-c5-gateway; NS=llm-c5-gateway; URL=http://localhost:8010;  AUTH=yes ;;
  c6-all)      OVERLAY=kind-secure;     NS=llm-secure;     URL=https://localhost:8443; AUTH=yes ;;
  *) echo "unknown config: $CONFIG" >&2; exit 1 ;;
esac

echo "== switching to $CONFIG ($NS)"
for n in $ALL_NS; do
  if [ "$n" != "$NS" ] && kubectl get ns "$n" >/dev/null 2>&1; then
    ./scripts/pause-env.sh "$n" >/dev/null
  fi
done

./scripts/resume-env.sh "kubernetes/overlays/$OVERLAY" "$NS"

if ! kubectl -n "$NS" exec deploy/ollama -- ollama list | grep -q "$MODEL"; then
  ./scripts/pull-model.sh "$NS" "kubernetes/overlays/$OVERLAY"
fi

unset AUTH_TOKEN K6_INSECURE_SKIP_TLS_VERIFY
export BASE_URL="$URL"
if [ "$AUTH" = "yes" ]; then
  AUTH_TOKEN="$(grep '^API_KEY=' kubernetes/components/gateway/gateway.env | cut -d= -f2)"
  export AUTH_TOKEN
fi
case "$URL" in https://*) export K6_INSECURE_SKIP_TLS_VERIFY=true ;; esac

export WARMUP="${WARMUP:-2m}"
./scripts/run-experiment.sh "$EXP" "$CONFIG" "$REP" "$NS"
RATE=50 DURATION=2m ./scripts/run-experiment.sh "$EXP" "${CONFIG}-health" "$REP" "$NS" tests/k6/health-path.js
