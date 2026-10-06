#!/usr/bin/env bash
# Scale an environment to zero (keeps PVC/model). Usage: pause-env.sh <namespace>
# Only ONE environment (baseline OR secure) may run during a measurement.
set -euo pipefail
NS="${1:?usage: pause-env.sh <namespace>}"
kubectl -n "$NS" scale deploy --all --replicas=0
