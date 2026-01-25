# Quick Deployment Fix Summary

> **NOTE**: This document was updated after discovering the two-domain architecture. 
> See **[CADDY_API_FIX.md](./CADDY_API_FIX.md)** for the complete discovery story and final architecture.

## What Was Fixed

Both **Swagger UI** and **Next.js** were failing to communicate with the API server in Podman because they were using the wrong URLs.

## Root Cause

Both Next.js and API server run in the **same container**, but Caddy routes them via **separate domains**:
- `https://ecomm.40b5c371.nip.io` → Next.js frontend (port 3002)
- `https://ecomm-api.40b5c371.nip.io` → Express API server (port 3003)

Client-side code (browser) should use `https://ecomm-api.40b5c371.nip.io` for all API calls.

## The Fix

### 1. Configure Frontend to Use Dedicated API Domain
Frontend now calls the dedicated API domain instead of the Next.js domain:
- **Client-side (browser)**: `NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io`
- **Caddy routing**: `ecomm-api.40b5c371.nip.io` → Express API server (port 3003)

### 2. Simplified API Client
Removed unnecessary SSR complexity since frontend uses client-side rendering only (`'use client'`).

### 3. Swagger UI for SSH Access
Updated OpenAPI spec with `http://localhost:3003` for secure SSH port forwarding access.

## Deploy to OCI VM

### Prerequisites

**CRITICAL**: `.env.oci` must exist in `docker/` directory with `NEXT_PUBLIC_API_URL` set **before building**:

```bash
# .env.oci must include (along with other vars):
NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io
```

**Why**: `NEXT_PUBLIC_API_URL` is embedded into the Next.js JavaScript bundle at **build time**, not runtime. 
The build process reads this from `.env.oci` and compiles it into the client-side code.

### Quick Steps

```bash
# 1. SSH to VM
ssh opc@<vm-ip>

# 2. Pull latest code
cd ~/compose/demo/oracle-demo-ecomm
git pull origin main

# 3. Verify .env.oci has build-time variables
cd docker
grep NEXT_PUBLIC_API_URL .env.oci
# Should show: NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io

# 4. Rebuild and restart (reads .env.oci during build)
podman-compose -f podman-compose.yml down
podman-compose -f podman-compose.yml build --no-cache
podman-compose -f podman-compose.yml up -d

# 5. Verify logs
podman logs ecomm --tail 50
```

### Expected Log Output

```
============================================================
Churn Model API Server
============================================================
Server running on http://localhost:3001
Swagger UI available at http://localhost:3001/api-docs
============================================================
Database connection: SUCCESS
============================================================

  ▲ Next.js 15.1.4
  - Local:        http://localhost:3000

 ✓ Starting...
 ✓ Ready in 2s
```

### Test Everything

```bash
# From VM (internal URLs)
curl http://localhost:3003/api/health
curl http://localhost:3002

# From browser (public URLs)
https://ecomm.40b5c371.nip.io                    # Frontend (Next.js)
https://ecomm-api.40b5c371.nip.io/api/health     # API (Express)
# Swagger UI: SSH port forward only (http://localhost:3003/api-docs)
```

## Architecture Diagram

```
┌────────────────────────────────────────────────────────┐
│  Container: ecomm                                      │
│                                                        │
│  ┌──────────────────┐    ┌──────────────────┐         │
│  │ Next.js          │───▶│ API Server       │         │
│  │ Port 3000        │    │ Port 3001        │         │
│  │                  │    │ (with Swagger)   │         │
│  │ Server-side:     │    │                  │         │
│  │ Uses API_URL     │    │                  │         │
│  │ http://localhost │    │                  │         │
│  │      :3001       │    │                  │         │
│  │                  │    │                  │         │
│  │ Client-side:     │    │                  │         │
│  │ Uses             │    │                  │         │
│  │ NEXT_PUBLIC_     │    │                  │         │
│  │ API_URL (public) │    │                  │         │
│  └──────────────────┘    └──────────────────┘         │
│         │                          │                  │
└─────────┼──────────────────────────┼──────────────────┘
          │                          │
     Host Port                  Host Port
       3002                        3003
          │                          │
          └──────────┬───────────────┘
                     │
              Caddy Reverse Proxy
                   │
       ┌───────────┴───────────┐
       │                       │
ecomm.40b5c371.nip.io   ecomm-api.40b5c371.nip.io
(Frontend: Port 3002)   (API: Port 3003)
       │                       │
       └───────────┬───────────┘
                   │
                 Browser
       (Calls both domains)
```

## Files Changed

1. ✅ `server/openapi.ts` - Dynamic server URLs
2. ✅ `app/lib/api/churn-api.ts` - Smart API client
3. ✅ `docker/podman-compose.yml` - Added `API_URL` env var
4. ✅ `docker/.env.oci.example` - Documented `PUBLIC_API_URL`
5. ✅ `FIX_SWAGGER_PODMAN.md` - Complete troubleshooting guide

## Verification Checklist

After deployment, verify:

- [ ] Container is running: `podman ps | grep ecomm`
- [ ] Logs show both servers started: `podman logs ecomm --tail 50`
- [ ] Frontend loads: `https://ecomm.40b5c371.nip.io`
- [ ] API responds: `https://ecomm-api.40b5c371.nip.io/api/health`
- [ ] Swagger UI (via SSH): `ssh -L 3003:localhost:3003` then `http://localhost:3003/api-docs`
- [ ] Swagger "Try it out" works with `localhost:3003` server selected
- [ ] Dashboard loads data (browser calls ecomm-api domain)

## Troubleshooting

### Swagger still shows "Failed to fetch"

```bash
# Check NEXT_PUBLIC_API_URL is set in container
podman exec ecomm env | grep NEXT_PUBLIC_API_URL

# If not found, add to docker/.env.oci on VM:
echo "NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io" >> docker/.env.oci

# Then rebuild
podman-compose -f podman-compose.yml down
podman-compose -f podman-compose.yml up -d app
```

### Next.js can't fetch data

```bash
# Check API_URL is set
podman exec ecomm env | grep API_URL

# Should show:
# API_URL=http://localhost:3001

# If not, check podman-compose.yml has:
# environment:
#   API_URL: "http://localhost:3001"
```

### Check Caddy routing

```bash
# View Caddy config
sudo cat /etc/caddy/Caddyfile

# Check Caddy is running
sudo systemctl status caddy

# View Caddy logs
sudo journalctl -u caddy -n 30 --no-pager
```

## Why This Works

### Before Fix ❌

```
Browser loads: https://ecomm.40b5c371.nip.io (frontend)
        ↓
Frontend tries to call: https://ecomm.40b5c371.nip.io/api/recommender/product
        ↓
Caddy routes to: Next.js (port 3002)
        ↓
Next.js looks for: app/api/recommender/product/route.ts
        ↓
FAILS: File doesn't exist (only in Express server!)
```

### After Fix ✅

```
Browser loads: https://ecomm.40b5c371.nip.io (frontend)
        ↓
Frontend calls: https://ecomm-api.40b5c371.nip.io/api/recommender/product
        ↓
Caddy routes to: Express API (port 3003)
        ↓
Express handles: /api/recommender/product
        ↓
SUCCESS: Returns recommendations!

Swagger (via SSH tunnel):
Browser → http://localhost:3003/api-docs
        ↓
Swagger calls: http://localhost:3003/api/*
        ↓
SUCCESS: Secure access via SSH port forward
```

---

**Ready to deploy!** 🚀

Just pull, rebuild, and restart the container.
