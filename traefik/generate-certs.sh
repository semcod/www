#!/usr/bin/env bash
# Generate self-signed TLS certificate for local dev (semcod.localhost)
set -e

CERTS_DIR="$(dirname "$0")/certs"
mkdir -p "$CERTS"

if [ -f "$CERTS/local-cert.pem" ]; then
  echo "Certs already exist in $CERTS_DIR — skipping."
  echo "Delete them and re-run to regenerate."
  exit 0
fi

echo "Generating self-signed certificate for semcod.localhost ..."

openssl req -x509 -nodes \
  -days 365 \
  -newkey rsa:2048 \
  -keyout "$CERTS/local-key.pem" \
  -out "$CERTS/local-cert.pem" \
  -subj "/CN=semcod.localhost" \
  -addext "subjectAltName=DNS:semcod.localhost,DNS:localhost,IP:127.0.0.1"

echo "Done! Certs in $CERTS_DIR"
echo ""
echo "Add to your /etc/hosts if not already:"
echo "  127.0.0.1 semcod.localhost"
