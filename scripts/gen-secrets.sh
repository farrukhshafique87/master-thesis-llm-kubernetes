#!/usr/bin/env bash
# Create the git-ignored secret material used by the secure overlay:
#   - self-signed TLS certificate for localhost (lab use only)
#   - random API key for the gateway
# Existing files are kept unless you pass --force.
set -euo pipefail

cd "$(dirname "$0")/.."

TLS_DIR="kubernetes/components/ingress-tls"
GW_DIR="kubernetes/components/gateway"
FORCE="${1:-}"

if [ ! -f "$TLS_DIR/tls.crt" ] || [ "$FORCE" = "--force" ]; then
  openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
    -days 90 -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" \
    -keyout "$TLS_DIR/tls.key" -out "$TLS_DIR/tls.crt" 2>/dev/null
  chmod 600 "$TLS_DIR/tls.key"
  echo "created $TLS_DIR/tls.crt and tls.key (EC P-256, 90 days)"
else
  echo "kept existing TLS certificate"
fi

if [ ! -f "$GW_DIR/gateway.env" ] || [ "$FORCE" = "--force" ]; then
  umask 077
  echo "API_KEY=$(openssl rand -hex 32)" > "$GW_DIR/gateway.env"
  echo "created $GW_DIR/gateway.env"
else
  echo "kept existing gateway.env"
fi

echo
echo "For k6 against the secure setup:"
echo "  export AUTH_TOKEN=\$(grep '^API_KEY=' $GW_DIR/gateway.env | cut -d= -f2)"
echo "  export BASE_URL=https://localhost:8443"
echo "  export K6_INSECURE_SKIP_TLS_VERIFY=true"
