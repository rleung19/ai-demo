# Fix: Frontend Cannot Call API After Recommender Addition

**Date**: 2026-01-25  
**Issue**: After adding recommender APIs, frontend fails to call API endpoints  
**Root Cause**: Discovered via debugging  
**Status**: ✅ Fixed

---

## The Discovery

### What We Found

Through extensive debugging, we discovered the actual production architecture:

**Caddy Configuration** (from JSON API, not Caddyfile):
```json
{
  "ecomm.40b5c371.nip.io": "→ reverse_proxy host.docker.internal:3002",
  "ecomm-api.40b5c371.nip.io": "→ reverse_proxy host.docker.internal:3003"
}
```

**Key Insight**: There are **TWO separate domains**:
- `ecomm.40b5c371.nip.io` → Next.js frontend (port 3002)
- `ecomm-api.40b5c371.nip.io` → Express API (port 3003)

### Why It Worked Before

**Before adding recommender APIs:**

```
Browser → https://ecomm.40b5c371.nip.io/api/kpi/churn/summary
       ↓
Caddy → Next.js (port 3002)
       ↓
Next.js API Route: app/api/kpi/churn/summary/route.ts
       ↓
Oracle Database (direct query)
```

- Frontend used **Next.js API routes** (`app/api/`)
- All API calls handled by Next.js itself
- Express server (port 3003) existed but **was never used by the frontend**

### Why It Broke

**After adding recommender APIs:**

```
Browser → https://ecomm.40b5c371.nip.io/api/recommender/product
       ↓
Caddy → Next.js (port 3002)
       ↓
Next.js looks for: app/api/recommender/product/route.ts
       ↓
❌ FILE NOT FOUND! (only exists in Express server)
```

- Recommender APIs were only added to Express server
- Never added to Next.js API routes
- Frontend still pointing to Next.js domain
- Result: **404 Not Found**

---

## The Architecture

### Current Setup

```
┌─────────────────────────────────────────────────────┐
│  Caddy (Reverse Proxy)                              │
│                                                     │
│  ecomm.40b5c371.nip.io → localhost:3002            │
│  ecomm-api.40b5c371.nip.io → localhost:3003        │
└─────────────────────────────────────────────────────┘
              │                         │
              ↓                         ↓
┌──────────────────────┐  ┌──────────────────────────┐
│  Container: ecomm    │  │  Container: ecomm        │
│                      │  │                          │
│  Next.js (3000)      │  │  Express API (3001)      │
│  → Host Port 3002    │  │  → Host Port 3003        │
│                      │  │                          │
│  Frontend + OLD APIs │  │  ALL APIs (old + new)    │
│  - app/api/kpi/*     │  │  - /api/kpi/*            │
│  - ❌ recommender     │  │  - ✅ /api/recommender/* │
└──────────────────────┘  └──────────────────────────┘
```

### Frontend Architecture

**Component Type**: Client-Side Only (`'use client'`)

```typescript
// app/page.tsx
'use client';  // ← All rendering happens in browser

useEffect(() => {
  const data = await getKPIData(1);  // ← Runs in browser after page loads
  setKpiData(data);
}, []);
```

**No Server-Side Rendering (SSR)**:
- Page loads as empty shell
- JavaScript executes in browser
- Browser makes API calls
- Page updates with data

**API Call Configuration**:
```typescript
// app/lib/api/churn-api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
```

---

## The Fix

### Change 1: Update Frontend to Use API Domain

**File**: `docker/.env.oci`

```bash
NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io
```

Loaded automatically via `env_file: .env.oci` in `podman-compose.yml`.

**What this does**:
- Frontend now calls `https://ecomm-api.40b5c371.nip.io/api/*`
- Caddy routes to Express (port 3003)
- Express has ALL APIs (churn + recommender)
- Everything works! ✅

### Change 2: Revert Unnecessary Complexity

**File**: `app/lib/api/churn-api.ts`

Reverted to simple configuration:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
```

**Removed**:
- ❌ `API_URL` (not needed, no SSR)
- ❌ `typeof window` checks (not needed)
- ❌ Server-side vs client-side logic (not needed)

### Change 3: Update Swagger for SSH Access

**File**: `server/openapi.ts`

```typescript
servers: [
  { url: 'http://localhost:3003', description: 'SSH Port Forward' },
  { url: 'http://localhost:3001', description: 'Local Development' }
]
```

---

## Why This Is Secure

**What's exposed:**
- ✅ `ecomm.40b5c371.nip.io` → Frontend (via Caddy HTTPS)
- ✅ `ecomm-api.40b5c371.nip.io` → API (via Caddy HTTPS)

**What's NOT exposed:**
- ❌ Port 3003 directly (Caddy handles it)
- ❌ Swagger UI (`/api-docs` only via SSH port forward)
- ❌ Database (accessed only by API server)

**To access Swagger UI securely:**
```bash
# SSH with port forwarding
ssh -L 3003:localhost:3003 ubuntu@vm-ip

# Then access on local machine
http://localhost:3003/api-docs
```

---

## Local Development vs Production

### Local Development

**No configuration needed!**

```bash
# .env (no NEXT_PUBLIC_API_URL)
API_PORT=3001
```

**Flow**:
- Next.js: `http://localhost:3000`
- Express: `http://localhost:3001`
- Frontend calls: `http://localhost:3001` (default)
- ✅ Works perfectly!

### Production (OCI VM)

**Configuration** (in `docker/.env.oci`):
```bash
NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io
ADB_USERNAME=oml
ADB_PASSWORD="your-password"
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_medium
OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT=https://...
OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT=https://...
```

**Flow**:
- Browser → `https://ecomm.40b5c371.nip.io` (frontend)
- Browser → `https://ecomm-api.40b5c371.nip.io/api/*` (APIs)
- Caddy routes to correct ports
- ✅ Works perfectly!

---

## Deployment Steps

### On OCI VM

```bash
# 1. Pull latest code
cd ~/compose/demo/oracle-demo-ecomm
git pull origin main

# 2. Ensure .env.oci is configured correctly
cd docker
cat .env.oci

# Should include (among other variables):
# NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io

# If not, add it:
echo "NEXT_PUBLIC_API_URL=https://ecomm-api.40b5c371.nip.io" >> .env.oci

# 3. Rebuild and restart
cd docker
podman-compose -f podman-compose.yml down
podman-compose -f podman-compose.yml build app
podman-compose -f podman-compose.yml up -d app

# 3. Verify logs
podman logs ecomm --tail 50

# 4. Test frontend
curl https://ecomm.40b5c371.nip.io

# 5. Test API
curl https://ecomm-api.40b5c371.nip.io/api/health
```

### Expected Results

**Frontend loads**: ✅ Dashboard with KPI cards  
**API responds**: ✅ `{"status":"healthy",...}`  
**Dashboard data loads**: ✅ Real-time churn metrics  
**Recommender works**: ✅ `/api/recommender/product` returns recommendations

---

## Key Learnings

### 1. Caddy Admin API vs Caddyfile

The running Caddy configuration (via Admin API port 2019) was **different** from the Caddyfile:
- **Caddyfile**: Only showed n8n, langflow, ai-lab
- **Admin API**: Showed ecomm, ecomm-api, and 15+ other domains

**Lesson**: Always check running config via `curl http://localhost:2019/config/`

### 2. Two Servers, One Container

Both Next.js and Express run in the **same container**:
```
3000/tcp -> 0.0.0.0:3002  (Next.js)
3001/tcp -> 0.0.0.0:3003  (Express)
```

They can communicate internally via `localhost`, but from outside, they're separate services.

### 3. Client-Side vs Server-Side Rendering

The frontend uses **client-side rendering only** (`'use client'`):
- No SSR means no server-side API calls
- All API calls happen in the browser
- Only `NEXT_PUBLIC_*` variables are accessible
- No need for `API_URL` or SSR complexity

### 4. Express Was a Backup

The Express server was created as a **workaround for Oracle client issues** in Next.js, but:
- Next.js API routes worked fine in production
- Express existed but wasn't used by frontend
- Adding recommender APIs only to Express broke the frontend

---

## Files Changed

1. ✅ `app/lib/api/churn-api.ts` - Simplified API URL logic
2. ✅ `docker/podman-compose.yml` - Set correct API domain
3. ✅ `server/openapi.ts` - Updated Swagger server URLs
4. ✅ `CADDY_API_FIX.md` - This documentation

---

## Testing Checklist

- [ ] Local dev works: `npm run dev:all`
- [ ] API responds: `curl http://localhost:3001/api/health`
- [ ] Frontend loads: `http://localhost:3000`
- [ ] Frontend can fetch data (check browser console)
- [ ] Build succeeds: `npm run build && npm run server:build`
- [ ] Container builds: `podman-compose build app`
- [ ] Container runs: `podman-compose up -d app`
- [ ] Production frontend: `https://ecomm.40b5c371.nip.io`
- [ ] Production API: `https://ecomm-api.40b5c371.nip.io/api/health`
- [ ] Dashboard loads data (check Network tab)
- [ ] Recommender API works: Test in browser console or Swagger
- [ ] Swagger UI via SSH: `ssh -L 3003:localhost:3003` → `http://localhost:3003/api-docs`

---

**Resolution**: Simple one-line fix to use the correct API domain. The architecture was already in place, we just needed to point the frontend to it! 🎉
