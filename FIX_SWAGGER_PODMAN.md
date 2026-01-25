# Fix: API Communication Issues in Podman (Swagger UI + Next.js)

> **NOTE**: This document contains initial troubleshooting steps but may not reflect the final architecture. 
> See **[CADDY_API_FIX.md](./CADDY_API_FIX.md)** for the complete, accurate picture of the two-domain setup 
> (`ecomm.40b5c371.nip.io` for frontend, `ecomm-api.40b5c371.nip.io` for API).

## The Problems

### 1. Swagger UI "Failed to fetch"
When accessing Swagger UI through the containerized deployment, the "Try it out" feature fails with:
```
Failed to fetch.
Possible Reasons: CORS / Network Failure / URL scheme must be "http" or "https"
```

### 2. Next.js Cannot Call API Server
Next.js server-side rendering (SSR) fails to fetch data from the API server.

**Root Causes**: 
1. OpenAPI spec was hardcoded to `http://localhost:3001`
2. Next.js was using the same URL for both server-side (should use internal) and client-side (should use public) API calls

## Understanding the Architecture

### Container Communication

Both Next.js and the API server run in the **same container**, but are accessed via **two separate domains**:

```
┌─────────────────────────────────────────┐
│  Container (ecomm)                      │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ Next.js      │    │ Express API  │  │
│  │ Port 3000    │    │ Port 3001    │  │
│  │ (Frontend)   │    │ (All APIs)   │  │
│  └──────────────┘    └──────────────┘  │
│       │                    │            │
└───────┼────────────────────┼────────────┘
        │                    │
    Host Port              Host Port
      3002                   3003
        │                    │
        │                    │
┌───────┴────────────────────┴───────────┐
│       Caddy Reverse Proxy              │
│                                        │
│  ecomm.40b5c371.nip.io                 │
│    → localhost:3002 (Next.js)          │
│                                        │
│  ecomm-api.40b5c371.nip.io             │
│    → localhost:3003 (Express API)      │
└────────────────────────────────────────┘
         ↑                    ↑
         │                    │
    Frontend Domain      API Domain
```

### API Access Architecture

**Client-side (Browser) - ACTUAL USAGE**:
- Frontend loads from: `https://ecomm.40b5c371.nip.io` (Next.js domain)
- API calls go to: `https://ecomm-api.40b5c371.nip.io` (Dedicated API domain)
- Uses `NEXT_PUBLIC_API_URL` environment variable
- Frontend uses client-side rendering only (`'use client'` - no SSR)

**Swagger UI Access (Secure)**:
- Access via SSH port forwarding only (not publicly exposed)
- Forward port: `ssh -L 3003:localhost:3003 user@vm`
- Access locally: `http://localhost:3003/api-docs`
- Swagger calls: `http://localhost:3003/api/*` (through SSH tunnel)

## The Solution

Made both OpenAPI server URL and Next.js API client **smart** based on context.

### What Changed

#### Fix 1: Dynamic OpenAPI Server URLs

**File**: `server/openapi.ts`

**Before**:
```typescript
servers: [
  {
    url: 'http://localhost:3001',  // ❌ Hardcoded
    description: 'Express API Server (local)',
  },
]
```

**After**:
```typescript
// Dynamic server configuration
function getServerUrls() {
  const servers = [];
  
  // Use public URL if available
  const publicUrl = process.env.NEXT_PUBLIC_API_URL || process.env.PUBLIC_API_URL;
  if (publicUrl) {
    servers.push({
      url: publicUrl,
      description: 'Production API (Public)',
    });
  }
  
  // Fallback to localhost with correct port
  const port = process.env.API_PORT || '3001';
  servers.push({
    url: `http://localhost:${port}`,
    description: 'Local Development',
  });
  
  return servers;
}

servers: getServerUrls(),  // ✅ Dynamic
```

#### Fix 2: Configure Frontend to Use Dedicated API Domain

**File**: `docker/.env.oci`

Added the dedicated API domain for browser requests:
```bash
NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io
```

**What this does**:
- Browser loads frontend from: `https://ecomm.40b5c371.nip.io`
- Browser makes API calls to: `https://ecomm-api.40b5c371.nip.io/api/*`
- Caddy routes `ecomm-api` domain to Express API server (port 3003)
- Express has ALL APIs including recommender endpoints

**File**: `app/lib/api/churn-api.ts`

Simplified (removed SSR complexity since frontend uses client-side rendering only):
```typescript
// Simple client-side configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
```

## Deployment Steps on OCI VM

### 1. Update `.env.oci`

Add the dedicated API domain URL:

```bash
cd ~/compose/demo/oracle-demo-ecomm/docker

# Edit .env.oci
nano .env.oci

# Add this line (use the ecomm-api domain, NOT ecomm):
NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io
```

Your `.env.oci` should now look like:
```bash
# API Domain - CRITICAL: Use ecomm-api domain!
NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io

# Database
ADB_USERNAME=oml
ADB_PASSWORD="your-password"
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_medium

# OCI Model Endpoints
OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT=https://...
OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT=https://...

# Container Runtime
NODE_ENV=production
TNS_ADMIN=/opt/oracle/wallet
ADB_WALLET_PATH=/opt/oracle/wallet
```

### 2. Pull Latest Code

```bash
cd ~/compose/demo/oracle-demo-ecomm
git pull origin main
```

### 3. Rebuild and Restart Container

```bash
cd docker

# Stop current container
podman-compose -f podman-compose.yml down

# Rebuild with new code
podman-compose -f podman-compose.yml build app

# Start container
podman-compose -f podman-compose.yml up -d app

# Verify it's running
podman logs --tail=50 ecomm
```

### 4. Test Swagger UI (Secure Access via SSH)

Swagger UI is **not publicly accessible** for security. Access it via SSH port forwarding:

```bash
# From your local machine:
ssh -L 3003:localhost:3003 ubuntu@vm-ip

# Then access locally:
http://localhost:3003/api-docs
```

**Expected Behavior**:
1. Swagger UI loads at `http://localhost:3003/api-docs`
2. At the top, you'll see a server dropdown with: **"SSH Port Forward (recommended for secure access)"** selected
3. "Try it out" buttons work!
4. API calls use `http://localhost:3003` (through SSH tunnel)

### 5. Verify API Endpoints

Test directly:
```bash
# From VM
curl https://ecomm-api.40b5c371.nip.io/api/health

# Should return:
# {"status":"healthy",...}

# Test frontend domain (should load Next.js app)
curl https://ecomm.40b5c371.nip.io

# Should return HTML
```

## Why This Works

### Container Architecture

```
Browser
  ↓
https://ecomm.40b5c371.nip.io/api-docs
  ↓
Nginx (public proxy)
  ↓
Container Port 3001 → Host Port 3003
  ↓
API Server (Express)
```

### Before Fix

1. Browser loads frontend from `https://ecomm.40b5c371.nip.io`
2. Frontend JavaScript tries to call: `https://ecomm.40b5c371.nip.io/api/recommender/product`
3. Caddy routes to: Next.js (port 3002)
4. Next.js looks for: `app/api/recommender/product/route.ts`
5. **FAILS**: File doesn't exist! (Recommender APIs only in Express)

### After Fix

1. Browser loads frontend from `https://ecomm.40b5c371.nip.io` (Next.js domain)
2. Frontend JavaScript calls: `https://ecomm-api.40b5c371.nip.io/api/recommender/product` (API domain)
3. Caddy routes `ecomm-api` to: Express (port 3003)
4. Express handles: `/api/recommender/product`
5. **SUCCESS**: Returns recommendations!

## For Next.js Frontend

The Next.js frontend now uses the dedicated API domain:
```bash
# In docker/.env.oci
NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io
```

This means:
- Frontend loads from: `https://ecomm.40b5c371.nip.io` (frontend domain)
- API calls go to: `https://ecomm-api.40b5c371.nip.io` (API domain)
- All APIs (churn + recommender) available via Express server
- Works from client-side rendering (frontend uses `'use client'` - no SSR)

## Local Development (No Changes Needed)

When running locally with `npm run start:all`:
- No `PUBLIC_API_URL` is set
- Falls back to `http://localhost:3001`
- Everything works as before ✅

## Troubleshooting

### Frontend can't load data

**Cause**: `NEXT_PUBLIC_API_URL` not set or set to wrong domain.

**Fix**:
```bash
# Verify env var is in container
podman exec ecomm env | grep NEXT_PUBLIC_API_URL

# Should show:
# NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io

# If not, add to docker/.env.oci and restart:
echo "NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io" >> docker/.env.oci
podman-compose down && podman-compose up -d
```

### "Try it out" works but returns 502/504

**Cause**: Nginx not routing correctly or API server not responding.

**Fix**:
```bash
# Check API is reachable from VM
curl http://localhost:3003/api/health

# Check Caddy routing for both domains
curl https://ecomm.40b5c371.nip.io  # Frontend
curl https://ecomm-api.40b5c371.nip.io/api/health  # API
```

### Server dropdown shows wrong URL

**Cause**: Browser cached old Swagger UI.

**Fix**:
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Or use Incognito/Private mode

## Checking Caddy Reverse Proxy Configuration

### View Caddy Configuration

```bash
# SSH to OCI VM
ssh opc@<vm-ip>

# View Caddy config
sudo cat /etc/caddy/Caddyfile

# Check running Caddy service
sudo systemctl status caddy

# View Caddy logs
sudo journalctl -u caddy -n 50 --no-pager
```

### Expected Caddy Configuration

Your Caddy should have TWO separate domains configured:

```caddy
# Frontend domain
ecomm.40b5c371.nip.io {
    reverse_proxy localhost:3002  # Next.js frontend
}

# Dedicated API domain (CRITICAL!)
ecomm-api.40b5c371.nip.io {
    reverse_proxy localhost:3003  # Express API server (all APIs)
}

# Note: Swagger UI (/api-docs) is NOT exposed publicly for security
# Access it via SSH port forwarding: ssh -L 3003:localhost:3003 user@vm
```

### Verify Port Mappings

```bash
# Check what's listening on host ports
sudo netstat -tlnp | grep -E ':(3002|3003)'

# Expected output:
# tcp  0  0  0.0.0.0:3002  0.0.0.0:*  LISTEN  <pid>/conmon
# tcp  0  0  0.0.0.0:3003  0.0.0.0:*  LISTEN  <pid>/conmon

# Check container port mappings
podman port ecomm

# Expected output:
# 3000/tcp -> 0.0.0.0:3002
# 3001/tcp -> 0.0.0.0:3003
```

### Test Routing

```bash
# From VM, test host ports directly
curl http://localhost:3002  # Should return Next.js HTML
curl http://localhost:3003/api/health  # Should return API health JSON

# Test through Caddy
curl https://ecomm.40b5c371.nip.io  # Frontend (Next.js)
curl https://ecomm-api.40b5c371.nip.io/api/health  # API (Express)
```

### Reload Caddy (if you make config changes)

```bash
# Edit config
sudo nano /etc/caddy/Caddyfile

# Validate config
sudo caddy validate --config /etc/caddy/Caddyfile

# Reload without downtime
sudo systemctl reload caddy

# Or restart if needed
sudo systemctl restart caddy
```

## Port Mapping Reference

| Service | Container Port | Host Port | Caddy Domain | Public URL |
|---------|---------------|-----------|--------------|------------|
| Next.js Frontend | 3000 | 3002 | ecomm.40b5c371.nip.io | https://ecomm.40b5c371.nip.io |
| Express API | 3001 | 3003 | ecomm-api.40b5c371.nip.io | https://ecomm-api.40b5c371.nip.io/api/* |
| Swagger UI | 3001 | 3003 | (none - SSH only) | http://localhost:3003/api-docs (SSH tunnel) |

**Key Points**: 
- Both servers run in the **same container**
- Two separate domains route to different ports
- Swagger UI not publicly exposed for security

---

**Date**: 2026-01-24  
**Issue**: Swagger UI and Next.js API communication failures in Podman  
**Fix**: Dynamic URLs for OpenAPI and smart API client  
**Status**: ✅ Ready to deploy
