#!/usr/bin/env bash
# Create the Kind cluster and install Calico. Idempotent-ish: skips creation if
# the cluster already exists.
set -euo pipefail

CLUSTER="thesis-cluster"
CALICO_VERSION="${CALICO_VERSION:-v3.32.2}"   # verify at docs.tigera.io, then pin

cd "$(dirname "$0")/.."

if kind get clusters | grep -qx "$CLUSTER"; then
  echo "Cluster $CLUSTER already exists - skipping creation"
else
  kind create cluster --config kind/kind-cluster.yaml
fi

kubectl config use-context "kind-$CLUSTER"

helm repo add projectcalico https://docs.tigera.io/calico/charts >/dev/null 2>&1 || true
helm repo update >/dev/null

if ! helm status calico -n tigera-operator >/dev/null 2>&1; then
  kubectl create namespace tigera-operator --dry-run=client -o yaml | kubectl apply -f -
  helm install calico projectcalico/tigera-operator \
    --version "$CALICO_VERSION" --namespace tigera-operator
fi

echo "Waiting for Calico and nodes (can take 2-4 min)..."
until kubectl get ns calico-system >/dev/null 2>&1; do sleep 5; done
kubectl -n calico-system rollout status ds/calico-node --timeout=300s
kubectl wait --for=condition=Ready nodes --all --timeout=300s
kubectl get nodes -o wide
