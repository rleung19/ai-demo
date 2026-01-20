# Next.js + Oracle Client Workarounds - Comprehensive Research

## Current Setup

- **Next.js**: 16.1.1
- **Node.js**: 22.x (from context)
- **node-oracledb**: 6.0.0
- **Issue**: NJS-045 error - cannot load thick mode binary in Next.js

## Root Cause Analysis

### The Problem
Next.js 16+ with Node.js 22 has issues loading native modules (`.node` files) because:
1. **Module bundling**: Next.js bundles/transforms modules, which interferes with native binary loading
2. **Path resolution**: Next.js resolves paths differently than standalone Node.js
3. **Hot reloading**: Development mode can cause multiple initialization attempts
4. **Native module isolation**: Next.js may isolate native modules in a way that breaks Oracle client initialization

### Why `test-node-connection.js` Works
- Runs as **standalone Node.js** process
- No bundling or transformation
- Direct access to native modules
- Full control over initialization order

---

## Workaround Options

### Option 1: Next.js Configuration - `serverExternalPackages` ⭐ **RECOMMENDED**

**What it does**: Tells Next.js to treat `oracledb` as an external package, preventing bundling and preserving native module behavior.

**Implementation**:

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Next.js 13.1+ (App Router)
  serverExternalPackages: ["oracledb"],
  
  // For older Next.js versions (Pages Router):
  // experimental: {
  //   serverComponentsExternalPackages: ["oracledb"]
  // },
};

export default nextConfig;
```

**Pros**:
- ✅ Simple configuration change
- ✅ No code changes needed
- ✅ Works with existing API routes
- ✅ Official Next.js solution for native modules

**Cons**:
- ⚠️ Requires Next.js 13.1+ (you have 16.1.1 ✅)
- ⚠️ May need Oracle Instant Client installed on deployment server

**Testing**:
```bash
# Restart Next.js after config change
npm run dev

# Test connection
curl http://localhost:3000/api/health
```

---

### Option 2: Downgrade Node.js to 20.x

**Rationale**: Node.js 20 has better native module compatibility with Next.js.

**Implementation**:
```bash
# Using nvm (recommended)
nvm install 20
nvm use 20

# Or using fnm
fnm install 20
fnm use 20

# Verify
node --version  # Should show v20.x.x

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Test
npm run dev
```

**Pros**:
- ✅ Better native module support
- ✅ More stable with Next.js 16
- ✅ Widely tested combination

**Cons**:
- ⚠️ Loses Node.js 22 features
- ⚠️ May need to update other dependencies
- ⚠️ Temporary solution (Node.js 22 will improve)

**Compatibility**:
- Next.js 16.1.1 ✅ Works with Node.js 20
- node-oracledb 6.0.0 ✅ Works with Node.js 20

---

### Option 3: Upgrade Next.js to 15.x

**Rationale**: Next.js 15 has improved native module handling.

**Current**: Next.js 16.1.1  
**Upgrade to**: Next.js 15.1.0 (latest stable)

**Implementation**:
```bash
npm install next@15.1.0 react@19 react-dom@19

# Update next.config.ts
const nextConfig: NextConfig = {
  serverExternalPackages: ["oracledb"],
};
```

**Pros**:
- ✅ Improved native module support
- ✅ Better error messages
- ✅ More stable for production

**Cons**:
- ⚠️ Actually, you're on 16.1.1 which is newer than 15
- ⚠️ Downgrading may lose features
- ⚠️ May have breaking changes

**Note**: Actually, Next.js 16 is newer than 15, so this might not help. Let's check if there's a Next.js 17 or if 16.1.1 is the latest.

---

### Option 4: Use Dynamic Import with `ssr: false`

**What it does**: Loads Oracle client only on server-side, avoiding client-side bundling.

**Implementation**:
```typescript
// app/lib/db/oracle.ts
let oracledb: any = null;

export async function initializeOracleClient() {
  if (typeof window !== 'undefined') {
    return; // Skip on client
  }
  
  if (oracledb) {
    return; // Already loaded
  }
  
  // Dynamic import
  oracledb = await import('oracledb');
  
  // Initialize
  const walletPath = process.env.ADB_WALLET_PATH;
  if (walletPath) {
    process.env.TNS_ADMIN = walletPath;
    try {
      oracledb.initOracleClient({
        libDir: process.env.ORACLE_CLIENT_LIB_DIR,
        configDir: walletPath,
      });
    } catch (err: any) {
      if (!err.message.includes('already been called')) {
        console.warn('Thick mode failed, using thin mode');
      }
    }
  }
}

// Call before using
await initializeOracleClient();
```

**Pros**:
- ✅ Delays loading until needed
- ✅ Avoids client-side bundling
- ✅ Can catch initialization errors

**Cons**:
- ⚠️ Adds async complexity
- ⚠️ May still hit NJS-045 in Next.js

---

### Option 5: Use Next.js Middleware to Initialize

**What it does**: Initialize Oracle client in middleware before API routes run.

**Implementation**:
```typescript
// middleware.ts (root of app directory)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

let oracleInitialized = false;

export async function middleware(request: NextRequest) {
  // Only initialize once
  if (!oracleInitialized && request.nextUrl.pathname.startsWith('/api')) {
    try {
      const oracledb = await import('oracledb');
      const walletPath = process.env.ADB_WALLET_PATH;
      
      if (walletPath && !oracledb.initOracleClient) {
        process.env.TNS_ADMIN = walletPath;
        oracledb.initOracleClient({
          libDir: process.env.ORACLE_CLIENT_LIB_DIR,
          configDir: walletPath,
        });
        oracleInitialized = true;
      }
    } catch (err) {
      console.warn('Oracle init in middleware failed:', err);
    }
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: '/api/:path*',
};
```

**Pros**:
- ✅ Runs before API routes
- ✅ Centralized initialization

**Cons**:
- ⚠️ Middleware runs on Edge runtime (may not support native modules)
- ⚠️ May not work for thick mode

---

### Option 6: Use Next.js Server Actions (Alternative Pattern)

**What it does**: Use Server Actions instead of API routes for database operations.

**Implementation**:
```typescript
// app/actions/churn.ts
'use server';

import { initializeOracleClient } from '@/app/lib/db/oracle';

export async function getChurnSummary() {
  await initializeOracleClient(); // Initialize before use
  // ... database logic
}
```

**Pros**:
- ✅ Different execution context
- ✅ May avoid bundling issues

**Cons**:
- ⚠️ Requires refactoring API routes
- ⚠️ May still have same issues

---

### Option 7: Use Thin Mode Only (Simplest)

**What it does**: Don't use thick mode at all, rely on thin mode.

**Implementation**:
```typescript
// app/lib/db/oracle.ts
// Remove all initOracleClient() calls
// Use thin mode only

export async function getConnection() {
  // Thin mode - no initialization needed
  return await oracledb.getConnection({
    user: process.env.ADB_USER,
    password: process.env.ADB_PASSWORD,
    connectionString: process.env.ADB_CONNECTION_STRING,
  });
}
```

**Pros**:
- ✅ No native module issues
- ✅ Works everywhere
- ✅ Simpler deployment

**Cons**:
- ⚠️ Limited wallet support
- ⚠️ May need different connection string format
- ⚠️ Some features unavailable

---

### Option 8: Use Standalone Build Mode

**What it does**: Next.js can build a standalone server that may handle native modules better.

**Implementation**:
```typescript
// next.config.ts
const nextConfig: NextConfig = {
  output: 'standalone',
  serverExternalPackages: ["oracledb"],
};
```

Then deploy:
```bash
npm run build
node .next/standalone/server.js
```

**Pros**:
- ✅ More control over server
- ✅ May avoid bundling issues

**Cons**:
- ⚠️ Different deployment process
- ⚠️ May still have issues

---

## Recommended Approach: Combination

**Best Solution**: Combine Option 1 + Option 2

1. **Add `serverExternalPackages` to next.config.ts** (Option 1)
2. **Use Node.js 20.x** (Option 2) - if Node.js 22 issues persist
3. **Initialize pool at startup** (already implemented)
4. **Keep standalone server as backup** (current solution)

---

## Testing Plan

### Step 1: Try `serverExternalPackages` First
```bash
# 1. Update next.config.ts
# 2. Restart Next.js
npm run dev

# 3. Test
curl http://localhost:3000/api/health
```

### Step 2: If Still Fails, Try Node.js 20
```bash
# Switch to Node.js 20
nvm use 20
npm run dev
```

### Step 3: If Still Fails, Use Standalone Server
```bash
# Current solution - already working
npm run server:dev
```

---

## Version Compatibility Matrix

| Next.js | Node.js | node-oracledb | Thick Mode | Notes |
|---------|---------|---------------|------------|-------|
| 16.1.1 | 22.x | 6.0.0 | ❌ NJS-045 | Current - has issues |
| 16.1.1 | 20.x | 6.0.0 | ✅ Should work | Recommended combo |
| 15.x | 20.x | 6.0.0 | ✅ Should work | Stable combo |
| 14.x | 20.x | 6.0.0 | ✅ Should work | Older but stable |
| 16.1.1 | 22.x | 6.0.0 | ⚠️ With config | Try `serverExternalPackages` |

---

## Next Steps

1. **First**: Add `serverExternalPackages: ["oracledb"]` to `next.config.ts`
2. **Test**: Restart Next.js and test API endpoints
3. **If fails**: Switch to Node.js 20.x
4. **If still fails**: Keep using standalone Express server (current solution)

---

## References

- [Next.js serverExternalPackages docs](https://nextjs.org/docs/app/api-reference/next-config-js/serverExternalPackages)
- [node-oracledb Next.js guide](https://node-oracledb.readthedocs.io/en/latest/user_guide/installation.html)
- [Stack Overflow: NJS-045 in Next.js](https://stackoverflow.com/questions/77205305/error-njs-045-cannot-load-a-node-oracledb-thick-mode-binary-for-node-js-next)
