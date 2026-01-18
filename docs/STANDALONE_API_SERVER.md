# Standalone Express API Server

## Overview

A standalone Express API server that provides the same endpoints as Next.js API routes, but runs separately to avoid Next.js native module issues with Oracle client.

## Why Use This?

- ✅ **Full thick mode support** - Oracle client works perfectly
- ✅ **No Next.js compatibility issues** - Runs as standalone Node.js process
- ✅ **Same API endpoints** - Drop-in replacement for Next.js API routes
- ✅ **Easy to test** - Can run alongside or instead of Next.js

## Quick Start

### Development Mode

```bash
npm run server:dev
```

Server runs on `http://localhost:3001` (or port specified in API_PORT env var) with hot reload.

### Production Mode

```bash
# Build
npm run server:build

# Start
npm run server:start
```

## API Endpoints

All endpoints are available:

- `GET /api/health` - Health check
- `GET /api/kpi/churn/summary` - Churn summary metrics
- `GET /api/kpi/churn/cohorts` - Cohort breakdown
- `GET /api/kpi/churn/metrics` - Model metrics
- `GET /api/kpi/churn/chart-data?type=distribution` - Chart data

## Configuration

The server uses the same `.env` file as Next.js:

```env
ADB_WALLET_PATH=/path/to/wallet
ADB_CONNECTION_STRING=hhzj2h81ddjwn1dm_medium
ADB_USERNAME=OML
ADB_PASSWORD=your_password
TNS_ADMIN=/path/to/wallet  # Optional, auto-set from ADB_WALLET_PATH
API_PORT=3001              # Optional, defaults to 3001
```

## Testing

```bash
# Start server
npm run server:dev

# In another terminal, test endpoints
curl http://localhost:3001/api/health
curl http://localhost:3001/api/kpi/churn/summary
curl http://localhost:3001/api/kpi/churn/cohorts
curl http://localhost:3001/api/kpi/churn/metrics
curl http://localhost:3001/api/kpi/churn/chart-data?type=distribution
```

## Integration with Next.js Frontend

### Option 1: Proxy from Next.js

Update `next.config.ts`:

```typescript
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/kpi/churn/:path*',
        destination: 'http://localhost:3001/api/kpi/churn/:path*',
      },
    ];
  },
};
```

### Option 2: Update API Client

Update `app/lib/api/churn-api.ts` to point to the standalone server:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
```

## File Structure

```
server/
├── index.ts              # Express app setup
├── routes/
│   ├── health.ts        # Health check route
│   └── churn/
│       ├── summary.ts   # Summary endpoint
│       ├── cohorts.ts   # Cohorts endpoint
│       ├── metrics.ts   # Metrics endpoint
│       └── chart-data.ts # Chart data endpoint
└── lib/
    ├── db/
    │   └── oracle.ts    # Database utilities (shared)
    └── api/
        ├── validation.ts # Request validation (shared)
        └── errors.ts     # Error handling (shared)
```

## Advantages Over Next.js API Routes

1. **Thick mode works** - No NJS-045 errors ✅
2. **Better performance** - Dedicated process for API
3. **Easier debugging** - Standard Express middleware
4. **Production ready** - Can deploy separately, scale independently

## Port Configuration

Default port is `3001`. Change via environment variable:

```bash
API_PORT=8080 npm run server:dev
```

Or add to `.env`:
```env
API_PORT=8080
```

**Note**: If `PORT` env var is set (e.g., by Next.js), it will be used. Set `API_PORT` explicitly to avoid conflicts.

## Troubleshooting

### Connection fails?

1. **Verify Oracle client is initialized**:
   Check server logs for "✓ Oracle client initialized (thick mode)"

2. **Check environment variables**:
   ```bash
   echo $ADB_WALLET_PATH
   echo $TNS_ADMIN
   ```

3. **Test standalone connection**:
   ```bash
   node scripts/test-node-connection.js
   ```

### Port already in use?

Change the port:
```bash
API_PORT=3002 npm run server:dev
```

## Production Deployment

1. **Build the server**:
   ```bash
   npm run server:build
   ```

2. **Set environment variables** on the server

3. **Start with PM2 or systemd**:
   ```bash
   pm2 start dist/server/index.js --name churn-api
   ```

4. **Configure reverse proxy** (nginx, etc.) to route `/api/kpi/churn/*` to the server
