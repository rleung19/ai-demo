# Fix: API Communication Issues in Podman (Swagger UI + Next.js)

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

Both Next.js and the API server run in the **same container**:

```
┌─────────────────────────────────────────┐
│  Container (ecomm)                      │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ Next.js      │───▶│ API Server   │  │
│  │ Port 3000    │    │ Port 3001    │  │
│  └──────────────┘    └──────────────┘  │
│       │                    │            │
└───────┼────────────────────┼────────────┘
        │                    │
    Host Port              Host Port
      3002                   3003
        │                    │
        └──────────┬─────────┘
                   │
              Caddy Reverse Proxy
                   │
         https://ecomm.40b5c371.nip.io
```

### Two Types of API Calls

**Server-side (Next.js SSR)**:
- Runs inside the container
- Should use `http://localhost:3001` (internal)
- Uses `API_URL` environment variable

**Client-side (Browser)**:
- Runs in user's browser
- Should use `https://ecomm.40b5c371.nip.io` (public)
- Uses `NEXT_PUBLIC_API_URL` environment variable

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

#### Fix 2: Smart Next.js API Client

**File**: `app/lib/api/churn-api.ts`

**Before**:
```typescript
// Always uses NEXT_PUBLIC_API_URL for both server and client
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
```

**After**:
```typescript
// Smart URL selection based on context
function getApiBaseUrl(): string {
  const isServer = typeof window === 'undefined';
  
  if (isServer) {
    // Server-side: Use internal container communication
    return process.env.API_URL || 'http://localhost:3001';
  } else {
    // Client-side: Use public URL for browser requests
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
  }
}

const API_BASE_URL = getApiBaseUrl();
```

**File**: `docker/podman-compose.yml`

Added separate environment variables:
```yaml
environment:
  API_URL: "http://localhost:3001"              # Server-side (internal)
  NEXT_PUBLIC_API_URL: "https://ecomm.40b5c371.nip.io"  # Client-side (public)
```

## Deployment Steps on OCI VM

### 1. Update `.env.oci`

Add the public API URL:

```bash
cd ~/compose/demo/oracle-demo-ecomm/docker

# Edit .env.oci
nano .env.oci

# Add this line at the top:
PUBLIC_API_URL=https://ecomm.40b5c371.nip.io
```

Your `.env.oci` should now look like:
```bash
PUBLIC_API_URL=https://ecomm.40b5c371.nip.io
ADB_USERNAME=oml
ADB_PASSWORD="your-password"
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_medium
OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT=https://...
OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT=https://...
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
podman logs ecomm --tail 50
```

### 4. Test Swagger UI

Access Swagger UI:
```
https://ecomm.40b5c371.nip.io/api-docs
```

**Expected Behavior**:
1. Swagger UI loads
2. At the top, you'll see a server dropdown with: **"Production API (Public)"** selected
3. "Try it out" buttons now work!
4. API calls use `https://ecomm.40b5c371.nip.io` instead of `http://localhost:3001`

### 5. Verify API Endpoints

Test directly:
```bash
# From VM
curl https://ecomm.40b5c371.nip.io/api/health

# Should return:
# {"status":"healthy",...}
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

1. Browser loads Swagger UI from `https://ecomm.40b5c371.nip.io/api-docs`
2. Swagger UI JavaScript tries to call APIs at `http://localhost:3001`
3. **FAILS**: Browser can't reach `localhost:3001` (it's inside the container!)

### After Fix

1. Browser loads Swagger UI from `https://ecomm.40b5c371.nip.io/api-docs`
2. Swagger UI JavaScript sees server URL: `https://ecomm.40b5c371.nip.io`
3. Swagger UI calls APIs at `https://ecomm.40b5c371.nip.io/api/*`
4. **SUCCESS**: Browser can reach the public URL!

## For Next.js Frontend

The Next.js frontend already uses `NEXT_PUBLIC_API_URL` correctly:
```yaml
# In podman-compose.yml
NEXT_PUBLIC_API_URL: "https://ecomm.40b5c371.nip.io"
```

This means:
- Next.js pages can call API endpoints via the public URL
- Works from both server-side (SSR) and client-side (browser)

## Local Development (No Changes Needed)

When running locally with `npm run start:all`:
- No `PUBLIC_API_URL` is set
- Falls back to `http://localhost:3001`
- Everything works as before ✅

## Troubleshooting

### Swagger still shows localhost:3001

**Cause**: Environment variable not loaded or container not rebuilt.

**Fix**:
```bash
# Verify env var is in container
podman exec ecomm env | grep PUBLIC_API_URL

# Should show:
# PUBLIC_API_URL=https://ecomm.40b5c371.nip.io

# If not, check .env.oci and restart container
```

### "Try it out" works but returns 502/504

**Cause**: Nginx not routing correctly or API server not responding.

**Fix**:
```bash
# Check API is reachable from VM
curl http://localhost:3003/api/health

# Check nginx routing
curl https://ecomm.40b5c371.nip.io/api/health
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

Your Caddyfile should have:

```caddy
ecomm.40b5c371.nip.io {
    reverse_proxy localhost:3002  # Next.js frontend
}

# OR if you want API accessible separately:
ecomm.40b5c371.nip.io {
    # Frontend
    reverse_proxy localhost:3002
    
    # API endpoints
    handle /api/* {
        reverse_proxy localhost:3003  # API server
    }
    
    handle /api-docs/* {
        reverse_proxy localhost:3003  # Swagger UI
    }
}
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
curl https://ecomm.40b5c371.nip.io  # Frontend
curl https://ecomm.40b5c371.nip.io/api/health  # API
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

| Service | Container Port | Host Port | Public URL |
|---------|---------------|-----------|------------|
| Next.js | 3000 | 3002 | https://ecomm.40b5c371.nip.io |
| API Server | 3001 | 3003 | https://ecomm.40b5c371.nip.io/api/* |
| Swagger UI | 3001 | 3003 | https://ecomm.40b5c371.nip.io/api-docs |

**Key Point**: Both servers run in the **same container** and can talk via `localhost` internally!

---

**Date**: 2026-01-24  
**Issue**: Swagger UI and Next.js API communication failures in Podman  
**Fix**: Dynamic URLs for OpenAPI and smart API client  
**Status**: ✅ Ready to deploy
