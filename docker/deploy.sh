#!/bin/bash
# Deployment script for OCI VM — Docker Compose or Podman Compose
# Rebuilds and restarts the ecomm container

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
  elif command -v podman-compose >/dev/null 2>&1; then
    podman-compose "$@"
  else
    echo "❌ ERROR: install Docker Compose or podman-compose"
    exit 1
  fi
}

resolve_compose_files() {
  COMPOSE_FILES=(-f docker-compose.yml)
  if [[ -f .env.oci ]] && grep -qE '^DB_BACKEND=postgres' .env.oci; then
    COMPOSE_FILES+=(-f docker-compose.postgres.yml)
    echo "📦 Compose profile: postgres"
  else
    COMPOSE_FILES+=(-f docker-compose.oracle.yml)
    echo "📦 Compose profile: oracle (ADB)"
  fi
}

echo "=========================================="
echo "Ecomm Container Deployment"
echo "=========================================="
echo ""

if [[ ! -f .env.oci ]]; then
  echo "❌ ERROR: .env.oci not found in docker/ directory"
  echo "   cp .env.oci.example .env.oci && edit secrets"
  exit 1
fi

if ! grep -q "NEXT_PUBLIC_API_URL=" .env.oci; then
  echo "⚠️  WARNING: NEXT_PUBLIC_API_URL not found in .env.oci"
  read -p "Continue anyway? (y/N): " -n 1 -r
  echo ""
  [[ $REPLY =~ ^[Yy]$ ]] || exit 1
fi

echo "📋 Configuration:"
grep "NEXT_PUBLIC_API_URL=" .env.oci || echo "   NEXT_PUBLIC_API_URL: (not set)"
grep "DB_BACKEND=" .env.oci || echo "   DB_BACKEND: oracle (default)"
echo ""

resolve_compose_files

echo "📤 Exporting build-time variables from .env.oci..."
export $(grep "^NEXT_PUBLIC_API_URL=" .env.oci | xargs)
if grep -q "^NEXT_PUBLIC_AGENTIC_FLOW_WEBHOOK_URL=" .env.oci; then
  export $(grep "^NEXT_PUBLIC_AGENTIC_FLOW_WEBHOOK_URL=" .env.oci | xargs)
fi
echo "✅ NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-<not set>}"
echo ""

echo "🛑 Stopping existing container..."
compose "${COMPOSE_FILES[@]}" down
echo ""

echo "🔨 Rebuilding image..."
compose "${COMPOSE_FILES[@]}" build --no-cache
echo ""

echo "🚀 Starting container..."
compose "${COMPOSE_FILES[@]}" up -d
echo ""

echo "⏳ Waiting for health check..."
sleep 5

echo "📄 Recent logs:"
echo "=========================================="
if command -v podman >/dev/null 2>&1 && podman ps --format '{{.Names}}' 2>/dev/null | grep -q '^ecomm$'; then
  podman logs --tail=30 ecomm
elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^ecomm$'; then
  docker logs --tail=30 ecomm
fi
echo "=========================================="
echo ""

echo "✅ Deployment complete!"
echo ""
echo "🌐 Host ports:"
echo "   UI:  http://localhost:3002  (→ container :3000)"
echo "   API: http://localhost:3003/api/health  (→ container :3001)"
echo ""
echo "   Production (via Caddy):"
echo "   Frontend: https://ecomm.40b5c371.nip.io"
echo "   API:      https://ecomm-api.40b5c371.nip.io/api/health"
echo ""
echo "📊 Commands:"
echo "   Logs:   podman logs -f ecomm   # or: docker logs -f ecomm"
echo "   Status: podman ps               # or: docker ps"
echo ""

read -p "📺 Follow logs now? [Y/n]: " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
  if command -v podman >/dev/null 2>&1; then
    podman logs -f ecomm
  else
    docker logs -f ecomm
  fi
fi
