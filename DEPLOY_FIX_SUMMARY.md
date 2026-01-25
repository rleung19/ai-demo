# Quick Deployment Fix Summary

## What Was Fixed

Both **Swagger UI** and **Next.js** were failing to communicate with the API server in Podman because they were using the wrong URLs.

## Root Cause

Both Next.js and API server run in the **same container**, but:
- Server-side code (Next.js SSR) should use `http://localhost:3001` (internal)
- Client-side code (browser) should use `https://ecomm.40b5c371.nip.io` (public)

Previously, everything used the same `NEXT_PUBLIC_API_URL` for both contexts.

## The Fix

### 1. Smart Next.js API Client
Now detects if code is running on server or client and uses the appropriate URL:
- **Server-side**: `API_URL=http://localhost:3001`
- **Client-side**: `NEXT_PUBLIC_API_URL=https://ecomm.40b5c371.nip.io`

### 2. Dynamic OpenAPI Spec
Swagger UI now uses the public URL when available via `PUBLIC_API_URL` environment variable.

## Deploy to OCI VM

### Quick Steps

```bash
# 1. SSH to VM
ssh opc@<vm-ip>

# 2. Pull latest code
cd ~/compose/demo/oracle-demo-ecomm
git pull origin main

# 3. Rebuild and restart
cd docker
podman-compose -f podman-compose.yml down
podman-compose -f podman-compose.yml build app
podman-compose -f podman-compose.yml up -d app

# 4. Verify logs
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
https://ecomm.40b5c371.nip.io                    # Frontend
https://ecomm.40b5c371.nip.io/api/health         # API
https://ecomm.40b5c371.nip.io/api-docs           # Swagger UI
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
           https://ecomm.40b5c371.nip.io
                     │
                   Browser
                     │
              (Uses public URLs)
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
- [ ] API responds: `https://ecomm.40b5c371.nip.io/api/health`
- [ ] Swagger UI loads: `https://ecomm.40b5c371.nip.io/api-docs`
- [ ] Swagger "Try it out" works (no CORS errors)
- [ ] Dashboard loads data (Next.js can call API)

## Troubleshooting

### Swagger still shows "Failed to fetch"

```bash
# Check PUBLIC_API_URL is set in container
podman exec ecomm env | grep PUBLIC_API_URL

# If not found, add to docker/.env.oci on VM:
echo "PUBLIC_API_URL=https://ecomm.40b5c371.nip.io" >> docker/.env.oci

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
Browser → Swagger UI loads
        ↓
Swagger tries to call: http://localhost:3001
        ↓
FAILS: Browser can't reach container's localhost

Next.js SSR → Tries to call: https://ecomm.40b5c371.nip.io
        ↓
SLOW: Goes through external network instead of internal
```

### After Fix ✅

```
Browser → Swagger UI loads
        ↓
Swagger calls: https://ecomm.40b5c371.nip.io/api/*
        ↓
SUCCESS: Browser reaches public URL → Caddy → Container

Next.js SSR → Calls: http://localhost:3001
        ↓
SUCCESS: Internal container communication (fast!)

Browser → JavaScript calls: https://ecomm.40b5c371.nip.io/api/*
        ↓
SUCCESS: Public URL works from browser
```

---

**Ready to deploy!** 🚀

Just pull, rebuild, and restart the container.
