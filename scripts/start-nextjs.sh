#!/bin/bash
# Start Next.js development server with Oracle environment variables
# This ensures TNS_ADMIN is set for thin mode wallet access

# Load environment variables from .env file
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

# Ensure TNS_ADMIN is set (critical for thin mode wallet access)
if [ -z "$TNS_ADMIN" ] && [ -n "$ADB_WALLET_PATH" ]; then
  export TNS_ADMIN="$ADB_WALLET_PATH"
  echo "✓ Set TNS_ADMIN to: $TNS_ADMIN"
fi

# Start Next.js
echo "Starting Next.js development server..."
echo "TNS_ADMIN: $TNS_ADMIN"
echo "ADB_CONNECTION_STRING: $ADB_CONNECTION_STRING"
npm run dev
