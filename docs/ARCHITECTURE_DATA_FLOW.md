# Architecture and Data Flow

## Current Setup (Express Server - Port 3001)

```
┌─────────────┐
│   Browser   │
│  (Client)   │
└──────┬──────┘
       │
       │ HTTP Request
       │ http://localhost:3001/api/kpi/churn/*
       │
       ▼
┌─────────────────────┐
│  Express Server     │
│  Port 3001          │
│  (Standalone)       │
└──────┬──────────────┘
       │
       │ Database Query
       │
       ▼
┌─────────────────────┐
│  Oracle Database    │
│  (ADB)              │
└─────────────────────┘

Next.js Server (Port 3000)
└── Only serves the frontend HTML/JS/CSS
    └── Does NOT handle API requests
```

**Key Points:**
- Browser talks **DIRECTLY** to Express server (port 3001)
- Next.js server (port 3000) is **NOT** involved in API calls
- No proxy - direct connection from browser to Express
- Express server talks directly to Oracle database

## Alternative Setup (Next.js API Routes)

```
┌─────────────┐
│   Browser   │
│  (Client)   │
└──────┬──────┘
       │
       │ HTTP Request
       │ /api/kpi/churn/* (same origin, port 3000)
       │
       ▼
┌─────────────────────┐
│  Next.js Server     │
│  Port 3000          │
│  ┌───────────────┐  │
│  │ API Routes    │  │
│  │ (App Router)  │  │
│  └───────┬───────┘  │
└──────────┼──────────┘
           │
           │ Database Query
           │
           ▼
┌─────────────────────┐
│  Oracle Database    │
│  (ADB)              │
└─────────────────────┘

Express Server (Port 3001)
└── Not running (or running but not used)
```

**Key Points:**
- Browser talks to **Next.js API routes** (same origin, port 3000)
- Next.js API routes talk directly to Oracle database
- Express server is **NOT** involved
- No proxy - Next.js handles everything

## Configuration

The routing is controlled by `API_BASE_URL` in `app/lib/api/churn-api.ts`:

### Current (Express Server):
```typescript
const API_BASE_URL = 'http://localhost:3001';
// Browser → http://localhost:3001/api/kpi/churn/*
```

### Alternative (Next.js API Routes):
```typescript
const API_BASE_URL = '';  // Empty string = same origin
// Browser → /api/kpi/churn/* (relative path, same origin)
```

## Important Notes

1. **No Proxy Pattern**: Next.js API routes do NOT proxy to Express server. They are **separate implementations** of the same endpoints.

2. **Two Independent Implementations**:
   - `app/api/kpi/churn/*` - Next.js API routes (App Router)
   - `server/routes/churn/*` - Express routes
   - Both implement the same endpoints but are completely independent

3. **Browser Always Makes the Call**: The browser (client-side JavaScript) always makes the HTTP request. It either:
   - Goes directly to Express (current setup)
   - Goes to Next.js API routes (alternative setup)

4. **Server-Side Rendering**: If you were using Server Components or Server Actions, Next.js server would make the call. But currently, all API calls are made from client-side code (`'use client'` components).

## Data Flow Summary

### Current Setup (Express):
```
Browser (Client) 
  → fetch('http://localhost:3001/api/kpi/churn/summary')
    → Express Server (Port 3001)
      → Oracle Database
        → Response
          → Express Server
            → Browser
```

### Alternative Setup (Next.js):
```
Browser (Client)
  → fetch('/api/kpi/churn/summary')  // Same origin
    → Next.js Server (Port 3000)
      → API Route Handler
        → Oracle Database
          → Response
            → Next.js Server
              → Browser
```

## Why Two Implementations?

1. **Development Flexibility**: Compare behavior between Next.js and Express
2. **Fallback Option**: If Next.js has issues, can switch to Express
3. **Testing**: Easier to test Express server independently
4. **Oracle Connection Issues**: Express server works better with Oracle native modules

## Switching Between Implementations

See [API_SERVER_SWITCH.md](API_SERVER_SWITCH.md) for detailed instructions.

## API Request Timeouts

**Default Timeout: 10 seconds (10000ms)**

All API calls use a 10-second timeout to accommodate database queries:
- KPI API calls: 10 seconds timeout, 3 retries (total possible wait: ~40 seconds)
- Health check: 10 seconds timeout, 1 retry (total possible wait: ~20 seconds)

The timeout is configured in `app/lib/api/churn-api.ts`:
```typescript
async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retries = 3,
  timeout = 10000  // 10 seconds for database queries
)
```

**Why 10 seconds?**
- Oracle database queries can take 3-5 seconds
- Network latency adds additional time
- 5 seconds was too short, causing premature timeouts and retries
