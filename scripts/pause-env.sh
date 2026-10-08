#!/usr/bin/env bash
# Stop an environment but keep its volume and model. Usage: pause-env.sh <namespace>
# Only one environment may run during a measurement. The Ingress and any
# NodePort Service are removed too: NodePort numbers are unique cluster-wide and
# two Ingress objects for the same host would compete. resume-env.sh recreates them.
set -euo pipefail
NS="${1:?usage: pause-env.sh <namespace>}"
kubectl -n "$NS" scale deploy --all --replicas=0
kubectl -n "$NS" delete ingress --all --ignore-not-found
kubectl -n "$NS" get svc --no-headers | awk '$2=="NodePort"{print $1}' \
  | xargs -r kubectl -n "$NS" delete svc
