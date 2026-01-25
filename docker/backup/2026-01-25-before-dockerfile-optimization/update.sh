#!/bin/bash
# Update and deploy script for OCI VM
# Pulls latest code from git, then rebuilds and restarts container

set -e  # Exit on error

echo "=========================================="
echo "Ecomm Update & Deployment"
echo "=========================================="
echo ""

# Step 1: Go to project root
cd ..

# Step 2: Pull latest code
echo "📥 Pulling latest code from git..."
git pull origin main
echo "✅ Code updated"
echo ""

# Step 3: Go back to docker directory
cd docker

# Step 4: Run deployment script
echo "🚀 Starting deployment..."
echo ""
./deploy.sh
