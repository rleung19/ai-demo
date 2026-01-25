# Swagger Dynamic Server URL - Debug Testing

## The Bug

When accessing Swagger via SSH port forward at `http://localhost:3003/api-docs`, the server dropdown was showing:
- ❌ `https://ecomm-api.40b5c371.nip.io` (production URL - shouldn't show)
- ❌ `http://localhost:3001` (local dev - shouldn't show)
- ❌ Missing: `http://localhost:3003` (the actual URL being accessed!)

## Root Cause

The original logic didn't use early returns, so it was falling through to the fallback condition even when it successfully detected localhost.

## The Fix

Updated `server/openapi.ts` to:
1. **Use early returns** - Return immediately after adding the appropriate server URL
2. **Add debug logging** - Console logs show which host is detected
3. **Clearer case handling** - Explicit if/return for each scenario

### Fixed Logic Flow

```typescript
function getServerUrls(req?: Request) {
  const host = req?.get('host');
  
  // Case 1: Production (non-localhost)
  if (host && !host.includes('localhost')) {
    servers.push({ url: `${protocol}://${host}`, ... });
    return servers; // ← Early return!
  }
  
  // Case 2: Localhost with port
  if (host && host.includes('localhost')) {
    const port = host.split(':')[1];
    if (port) {
      servers.push({ url: `http://localhost:${port}`, ... });
      return servers; // ← Early return!
    }
  }
  
  // Fallback: Only if no host detected
  // ... add production + localhost:3001
  return servers;
}
```

## Testing Checklist

### Test 1: SSH Port Forward (localhost:3003)
```bash
# Setup SSH tunnel
ssh -L 3003:localhost:3003 ubuntu@vm

# Access Swagger
open http://localhost:3003/api-docs
```

**Expected console output** (in terminal running server):
```
[OpenAPI] Request host: localhost:3003 protocol: http forwarded: undefined
[OpenAPI] Added localhost server: http://localhost:3003
```

**Expected server dropdown**:
- ✅ `http://localhost:3003 - Local (port 3003)` ← Only this one!

### Test 2: Local Development (localhost:3001)
```bash
# Start local dev
npm run dev:all

# Access Swagger
open http://localhost:3001/api-docs
```

**Expected console output**:
```
[OpenAPI] Request host: localhost:3001 protocol: http forwarded: undefined
[OpenAPI] Added localhost server: http://localhost:3001
```

**Expected server dropdown**:
- ✅ `http://localhost:3001 - Local (port 3001)` ← Only this one!

### Test 3: Production (via public domain)
```bash
# Access from browser
open https://ecomm-api.40b5c371.nip.io/api-docs
```

**Expected console output** (on OCI VM):
```
[OpenAPI] Request host: ecomm-api.40b5c371.nip.io protocol: http forwarded: https
[OpenAPI] Added production server: https://ecomm-api.40b5c371.nip.io
```

**Expected server dropdown**:
- ✅ `https://ecomm-api.40b5c371.nip.io - Current server (production)` ← Only this one!

### Test 4: Direct OpenAPI JSON endpoint
```bash
# Test the /openapi.json endpoint
curl http://localhost:3003/openapi.json | jq '.servers'
```

**Expected output**:
```json
[
  {
    "url": "http://localhost:3003",
    "description": "Local (port 3003)"
  }
]
```

## Debugging

If you still see wrong servers:

1. **Check console logs** - Look for the debug output in your terminal
2. **Verify host header** - Run: `curl -v http://localhost:3003/api-docs` and check the `Host:` header
3. **Check if req is undefined** - Debug log will show "Using fallback servers"
4. **Browser cache** - Hard refresh (Cmd+Shift+R) or open in incognito

## Removing Debug Logs

After confirming it works, remove these lines from `server/openapi.ts`:
```typescript
console.log('[OpenAPI] Request host:', host, 'protocol:', protocol, 'forwarded:', forwardedProto);
console.log('[OpenAPI] Added production server:', ...);
console.log('[OpenAPI] Added localhost server:', ...);
console.log('[OpenAPI] Using fallback servers (no host detected)');
```

## Expected Behavior Summary

| Access Method | URL | Shows in Dropdown |
|--------------|-----|-------------------|
| SSH tunnel | `http://localhost:3003/api-docs` | Only `http://localhost:3003` |
| Local dev | `http://localhost:3001/api-docs` | Only `http://localhost:3001` |
| Production | `https://ecomm-api.40b5c371.nip.io/api-docs` | Only `https://ecomm-api.40b5c371.nip.io` |

**No more confusion!** Each context shows exactly one relevant URL.
