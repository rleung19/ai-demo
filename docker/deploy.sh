#!/bin/bash
# Deployment script for OCI VM
# Rebuilds and restarts the ecomm container

set -e  # Exit on error

echo "=========================================="
echo "Ecomm Container Deployment"
echo "=========================================="
echo ""

# Check if .env.oci exists
if [ ! -f .env.oci ]; then
  echo "❌ ERROR: .env.oci not found in docker/ directory"
  echo "   Please create .env.oci with required variables"
  echo "   See .env.oci.example for reference"
  exit 1
fi

# Check if NEXT_PUBLIC_API_URL is set
if ! grep -q "NEXT_PUBLIC_API_URL=" .env.oci; then
  echo "⚠️  WARNING: NEXT_PUBLIC_API_URL not found in .env.oci"
  echo "   This is required for frontend to call the API"
  echo ""
  read -p "Continue anyway? (y/N): " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
  fi
fi

# Show current configuration
echo "📋 Configuration:"
grep "NEXT_PUBLIC_API_URL=" .env.oci || echo "   NEXT_PUBLIC_API_URL: (not set)"
echo ""

# Step 1: Stop existing container
echo "🛑 Stopping existing container..."
podman-compose -f podman-compose.yml down
echo "✅ Container stopped"
echo ""

# Step 2: Rebuild with no cache
echo "🔨 Rebuilding image (this may take a few minutes)..."
podman-compose -f podman-compose.yml build --no-cache
echo "✅ Image rebuilt"
echo ""

# Step 3: Start container
echo "🚀 Starting container..."
podman-compose -f podman-compose.yml up -d
echo "✅ Container started"
echo ""

# Step 4: Wait a moment for startup
echo "⏳ Waiting for services to start..."
sleep 3
echo ""

# Step 5: Show logs
echo "📄 Recent logs:"
echo "=========================================="
podman logs --tail=30 ecomm
echo "=========================================="
echo ""

# Step 6: Show status
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access points:"
echo "   Frontend:  https://ecomm.40b5c371.nip.io"
echo "   API:       https://ecomm-api.40b5c371.nip.io/api/health"
echo "   Swagger:   SSH tunnel → http://localhost:3003/api-docs"
echo ""
echo "📊 To view full logs: podman logs -f ecomm"
echo "🔍 To check status:   podman ps"
echo ""
