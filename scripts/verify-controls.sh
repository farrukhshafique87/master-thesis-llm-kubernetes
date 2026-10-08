#!/usr/bin/env bash
# Functional checks of the security controls in one namespace.
# Usage: verify-controls.sh <namespace>
# Checks only what is deployed in the namespace (RBAC objects, NetworkPolicies,
# gateway). Exit code 1 if any check fails.
set -uo pipefail
NS="${1:?usage: verify-controls.sh <namespace>}"
PASS=0
FAIL=0

# check "<description>" <yes|no> <command...>   (yes = command must succeed)
check() {
  local desc="$1" expected="$2" result
  shift 2
  if "$@" >/dev/null 2>&1; then result=yes; else result=no; fi
  if [ "$result" = "$expected" ]; then
    echo "PASS  $desc"
    PASS=$((PASS + 1))
  else
    echo "FAIL  $desc (expected $expected, got $result)"
    FAIL=$((FAIL + 1))
  fi
}

# HTTP GET from inside a pod: fetch <deployment> <url>
fetch() {
  kubectl -n "$NS" exec "deploy/$1" -- python -c \
    "import sys, urllib.request; urllib.request.urlopen(sys.argv[1], timeout=4)" "$2"
}

token_not_mounted() {
  [ "$(kubectl -n "$NS" get deploy "$1" -o jsonpath='{.spec.template.spec.automountServiceAccountToken}')" = "false" ]
}

if kubectl -n "$NS" get serviceaccount fastapi >/dev/null 2>&1; then
  echo "== RBAC"
  check "fastapi pod has no API token mounted" yes token_not_mounted fastapi
  check "fastapi service account cannot list pods" no \
    kubectl auth can-i list pods -n "$NS" --as="system:serviceaccount:$NS:fastapi"
  check "viewer group can read pods" yes \
    kubectl auth can-i get pods -n "$NS" --as=tester --as-group=llm-viewers
  check "viewer group cannot read secrets" no \
    kubectl auth can-i get secrets -n "$NS" --as=tester --as-group=llm-viewers
  check "viewer group cannot delete deployments" no \
    kubectl auth can-i delete deployments.apps -n "$NS" --as=tester --as-group=llm-viewers
fi

if kubectl -n "$NS" get networkpolicy -o name 2>/dev/null | grep -q .; then
  echo "== NetworkPolicies"
  check "api -> ollama is allowed" yes fetch fastapi http://ollama-service:11434/api/tags
  check "api -> internet is blocked" no fetch fastapi https://example.com
  if kubectl -n "$NS" get deploy gateway >/dev/null 2>&1; then
    check "gateway -> api is allowed" yes fetch gateway http://fastapi-service:8010/health
    check "gateway -> ollama is blocked" no fetch gateway http://ollama-service:11434/api/tags
  fi
fi

echo
echo "passed: $PASS  failed: $FAIL"
[ "$FAIL" -eq 0 ]
